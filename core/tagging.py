from abc import ABC, abstractmethod
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pprint import pp
import re
import statistics
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from google.cloud import language_v2

from core.book_store import BookStore
from core.utils import BoundedTokenBucket
from core.config import tagging as tagging_config
from core.config import book_store as bookstore_config


class TaggingPipeline(ABC):
    @abstractmethod
    def tag(self, text_parts: list[str]) -> tuple[list[dict], list[str]]:
        """Method to perform named entity recognition on the given text parts.

        Parameters
        ----------
        text_parts : list[str]
            List of text parts to be analyzed.

        Returns
        -------
        tuple[list[dict], list[str]]
            A tuple containing tagged entities and original text parts.
        """

        pass


class LocalModelTaggingPipeline(TaggingPipeline):
    def __init__(self, model_name: str, splitting_regex: str) -> None:
        """Initializes the LocalModelTaggingPipeline.

        Parameters
        ----------
        model_name : str
            Name of the pre-trained model to be used for tagging.
        splitting_regex : str
            Regular expression to split text into parts.

        Returns
        -------
        None
        """

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            model_name)
        self.tagging_pipeline = pipeline(
            'ner',
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy='simple'
        )
        self.splitting_regex = splitting_regex

    def tag(self, text: list[str] | str) -> tuple[list[dict], list[str]]:
        """Performs named entity recognition on the given text parts.

        Parameters
        ----------
        text :  list[str] | str
            Text or list of texts to be analyzed.

        Returns
        -------
        tuple[list[dict], list[str]]
            A tuple containing tagged entities and original text parts.
        """
        if isinstance(text, str):
            text = [text]

        text_parts = []

        print('Splitting content')
        for t in text:
            for t_part in re.split(self.splitting_regex, t):
                t_part = t_part.strip() if t_part else ''
                if len(t_part) > 10:
                    if len(t_part) > self.tokenizer.max_len_single_sentence:
                        # TODO: if possible, use the number of tokens instead of the number of characters (may be too expensive)
                        print(f'Warning : t_part length of {len(t_part)} is longer than max sentence length ({
                              self.tokenizer.max_len_single_sentence}), although it is probably okey since the tokenizer will merge characters')
                    text_parts.append(t_part)

        print('Tagging')
        tags = []
        for i, t_part in enumerate(tqdm(text_parts)):
            for tag in self.tagging_pipeline(t_part):
                tags.append({
                    'entity_group': tag['entity_group'],
                    'word': tag['word'],
                    'instance': {
                        'text_part': i,
                        'start': tag['start'],
                        'end': tag['end'],
                        'score': float(tag['score'])
                    }
                })
        return tags, text_parts


class GoogleNLPTaggingPipeline(TaggingPipeline):
    def __init__(self, splitting_regex: str) -> None:
        """Initializes the GoogleNLPTaggingPipeline.

        Parameters
        ----------
        splitting_regex : str
            Regular expression to split text into parts.

        Returns
        -------
        None
        """

        self.client = language_v2.LanguageServiceClient(
            client_options={"api_key": os.environ['GOOGLE_API_KEY']}
        )
        self.splitting_regex = splitting_regex
        self.token_bucket = BoundedTokenBucket(
            capacity=600, refill_interval=0.1)
        self.entity_names = [
            'UNKNOW',
            'PERSON',
            'LOCATION',
            'ORGANIZATION',
            'EVENT',
            'WORK_OF_ART',
            'CONSUMER_GOOD',
            'OTHER',
            'PHONE_NUMBER',
        ]
        self.entity_mapping = {
            'UNKNOW': 'MISC',
            'PERSON': 'PER',
            'LOCATION': 'LOC',
            'ORGANIZATION': 'ORG',
            'EVENT': 'MISC',
            'WORK_OF_ART': 'MISC',
            'CONSUMER_GOOD': 'MISC',
            'OTHER': 'MISC',
            'PHONE_NUMBER': 'MISC',
        }

    def tag(self, text: list[str] | str) -> tuple[list[dict], list[str]]:
        """Performs named entity recognition on the given text parts using Google Cloud NLP API.

        Parameters
        ----------
        text : list[str] | str
            Text or list of texts to be analyzed.

        Returns
        -------
        tuple[list[dict], list[str]]
            A tuple containing tagged entities and original text parts.
        """

        if isinstance(text, str):
            text = [text]
        text_parts = []

        print('Splitting content')
        for t in text:
            for t_part in re.split(self.splitting_regex, t):
                t_part = t_part.strip() if t_part else ''
                if len(t_part) > 10:
                    text_parts.append(t_part)

        print('Tagging')
        tags = []

        def process_text(t_part, i):
            # Account for google API rate limit (600 calls per minute)
            nonlocal tags

            while not self.token_bucket.consume(1):
                continue

            document = {
                "content": t_part,
                "type_": language_v2.Document.Type.PLAIN_TEXT,
                "language_code": 'fr'
            }
            response = self.client.analyze_entities(request={
                "document": document,
                "encoding_type": language_v2.EncodingType.UTF8
            })

            for entity in response.entities:
                for mention in entity.mentions:
                    if mention.type_ == language_v2.EntityMention.Type.PROPER:
                        tags.append({
                            'entity_group': self.entity_mapping[self.entity_names[entity.type_]],
                            'word': entity.name,
                            'instance': {
                                'text_part': i,
                                'start': mention.text.begin_offset,
                                'end': mention.text.begin_offset + len(entity.name),
                                'score': float(mention.probability)
                            }
                        })

        with ThreadPoolExecutor(max_workers=512) as executor:
            futures = []
            for i, t_part in enumerate(text_parts):
                futures.append(executor.submit(process_text, t_part, i))

            for future in tqdm(futures):
                future.result()

        self.token_bucket.stop()

        return tags, text_parts


class TagFilter(ABC):
    def __init__(self, grouped_tags: OrderedDict[str, OrderedDict[str, dict[str, int | float]]]) -> None:
        """Initializes the tag filter

        Parameters
        ----------
        grouped_tags : OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Unckecked tags

        Returns
        -------
        None
        """
        self.grouped_tags = grouped_tags

    @abstractmethod
    def filter(self) -> OrderedDict[str, OrderedDict[str, dict[str, int | float]]]:
        """Method to check tags based on various characteristics

        Returns
        -------
        OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Sub set of grouped_tags containing checked tags (modified or deleted)
        """
        pass


class MajorityClassCountTagFilter(TagFilter):
    def __init__(self, grouped_tags: OrderedDict[str, OrderedDict[str, dict[str, int | float]]], min_count: int) -> None:
        """Initializes the majority class count tag filter (cannot modify tags, only delete them)

        Parameters
        ----------
        grouped_tags : OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Unfiltered tags
        min_count : int
            Minimum number of occurences of the majority class to keep the tag

        Returns
        -------
        None
        """
        super().__init__(grouped_tags)
        self.min_count = min_count

    def filter(self) -> OrderedDict[str, OrderedDict[str, dict[str, int | float]]]:
        """Method to filter tags based on the majority class

        Returns
        -------
        OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Sub set of grouped_tags containing filtered tags only
        """

        filtered_tags = OrderedDict()

        for k, v in self.grouped_tags.items():
            if next(iter(v.values()))['count'] >= self.min_count:
                filtered_tags[k] = v

        return filtered_tags


class BlacklistTagFilter(TagFilter):
    def __init__(self, grouped_tags: OrderedDict[str, OrderedDict[str, dict[str, int | float]]], blacklist: list[str]) -> None:
        """Initializes the blacklist tag filter (cannot modify tags, only delete them)

        Parameters
        ----------
        grouped_tags : OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Unfiltered tags
        blacklist : list[str]
            list of regex that will not pass the filter

        Returns
        -------
        None
        """
        super().__init__(grouped_tags)
        self.blacklist = blacklist

    def filter(self) -> OrderedDict[str, OrderedDict[str, dict[str, int | float]]]:
        """Method to filter tags based on a blacklist of regex

        Returns
        -------
        OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Sub set of grouped_tags containing filtered tags only
        """

        filtered_tags = OrderedDict()
        for k, v in self.grouped_tags.items():
            if all([(not re.match(pattern, k)) for pattern in self.blacklist]):
                filtered_tags[k] = v

        return filtered_tags


class OpenAIFineTagger:
    def __init__(self, grouped_tags: OrderedDict[str, OrderedDict[str, dict[str, int | float]]], book_id: str, config: dict, book_store: BookStore) -> None:
        """Initializes the LLM fine tagger, it will check for low confidence tags and prompt a LLM about them

        Parameters
        ----------
        grouped_tags : OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Unchecked tags
        book_id : str
            Used to filter text chunks from the vector database
        config : dict
            Tagger config such as prompt_template, number of chunks, chunk size

        Returns
        -------
        None
        """
        self.grouped_tags = grouped_tags

        self.book_id = book_id
        self.book_store = book_store

        self.prompt_template = config['prompt_template']
        self.majority_class_threshold = config['majority_class_threshold']
        self.number_chunks = config['number_chunks']

        self.chunk_size = config['chunk_size']
        if self.chunk_size not in book_store.chunk_sizes:
            raise ValueError(f'{self.chunk_size} is not a valid chunk size')

        self.vector_db_query = config['vector_db_query']
        self.llm_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    def fine_tag(self) -> OrderedDict[str, OrderedDict[str, dict[str, int | float]]]:
        """Method to check tags and validate their class with a LLM

        Returns
        -------
        OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
            Sub set of grouped_tags containing checked tags only
        """
        fine_tags = dict()
        for k, v in self.grouped_tags.items():
            if next(iter(v.values()))['weight'] < self.majority_class_threshold:
                print(k)
                # retrieve chunks to feed to the LLM
                retrieved_chunks = book_store.retrieve_chunks(
                    book_id=self.book_id,
                    query=self.vector_db_query,
                    chunk_size=self.chunk_size,
                    max_retrieved_chunks=self.number_chunks,
                    contains_token=[k]
                )

                chunk_string = '\n---\n'.join(
                    [elem[0] for elem in retrieved_chunks]
                )

                prompt = self.prompt_template.format(
                    chunks=chunk_string,
                    entity=k
                )

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    n=1,
                    temperature=1.0,
                    top_p=1.0
                )
                llm_class = response.choices[0].message.content.strip()

                if llm_class not in ['PER', 'LOC', 'ORG', 'MISC']:
                    print(f'LLM output is malformed : {llm_class}')
                    tag_presence = [int((tag in llm_class))
                                    for tag in ['PER', 'LOC', 'ORG', 'MISC']]
                    if sum(tag_presence) == 1:
                        llm_class = ['PER', 'LOC', 'ORG',
                                     'MISC'][tag_presence.index(1)]
                        print(f'LLM output has been recovered : {llm_class}')
                    else:
                        print(f' LLM output : {
                              llm_class} is not valid and couln\'t be recovered')

                print(llm_class)
                print()
                fine_tags[k] = llm_class

        return fine_tags


def group_tags(raw_tags: list[dict]) -> tuple[OrderedDict, set]:
    """Groups raw tags by their entity group and calculate statistics for each group.

    Parameters
    ----------
    raw_tags : (list[dict])
        A list of dictionaries representing raw tags.

    Returns
    -------
    tuple[OrderedDict, set]
        A tuple containing the grouped tags and a set of unique entity groups.
    """

    print('Grouping tags')
    grouped_tags = dict()
    unique_entity_groups = set()
    scores = dict()
    for tag in raw_tags:
        entity_group = tag['entity_group']
        unique_entity_groups.add(entity_group)
        word = tag['word']
        if entity_group not in grouped_tags:
            grouped_tags[entity_group] = {}
            scores[entity_group] = {}
        if word not in grouped_tags[entity_group]:
            grouped_tags[entity_group][word] = {'instances': []}
            scores[entity_group][word] = {'scores': []}
        scores[entity_group][word]['scores'].append(
            float(tag['instance']['score'])
        )
        grouped_tags[entity_group][word]['instances'].append(
            tag['instance'])

        current_scores = scores[entity_group][word]['scores']
        grouped_tags[entity_group][word]['count'] = len(current_scores)
        grouped_tags[entity_group][word]['min'] = min(current_scores)
        grouped_tags[entity_group][word]['max'] = max(current_scores)
        grouped_tags[entity_group][word]['mean'] = statistics.mean(
            current_scores) if len(current_scores) > 1 else current_scores[0]
        grouped_tags[entity_group][word]['sdt'] = statistics.stdev(
            current_scores) if len(current_scores) > 1 else 0
        grouped_tags[entity_group][word]['median'] = statistics.median(
            current_scores) if len(current_scores) > 1 else current_scores[0]

    ordered_grouped_tags = OrderedDict()
    for entity_group, name_dict in grouped_tags.items():
        ordered_grouped_tags[entity_group] = OrderedDict(
            sorted(
                name_dict.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
        )
    return OrderedDict(sorted(ordered_grouped_tags.items(), key=lambda x: x[0])), unique_entity_groups


def group_tags_by_entity_names(grouped_tags: dict[str, dict]) -> OrderedDict[str, OrderedDict[str, dict[str, int | float]]]:
    """Group tags by entity name

    Parameters
    ----------
    grouped_tags : dict
        Tags grouped by entity group

    Returns
    -------
    OrderedDict[str, OrderedDict[str, dict[str, int | float]]]
        Tags grouped by entity name, with occurencre and a proportion associated with each class
    """

    entities = OrderedDict()
    for eg_key, eg_value in grouped_tags.items():
        for tag_key, tag_value in eg_value.items():
            if tag_key not in entities.keys():
                entities[tag_key] = OrderedDict()
            entities[tag_key][eg_key] = {
                'count': tag_value['count']
            }

    for k1, v1 in entities.items():
        total_count = sum([v['count'] for v in v1.values()])
        v1 = OrderedDict(sorted(
            v1.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        ))
        entities[k1] = v1
        for v2 in v1.values():
            v2['weight'] = v2['count'] / total_count

    entities = OrderedDict(sorted(
        entities.items(),
        key=lambda x: sum([v['count'] for v in x[1].values()]),
        reverse=True
    ))

    return (entities)


def load_book_raw_content(book_data: dict) -> list[str]:
    """Load the raw content of a book recursively from the given book data.

    Parameters
    ----------
    book_data : dict
        A dictionary containing book data.

    Returns
    -------
    list[str]
        A list containing the raw content of the book.
    """

    content = []

    def load_recursive(node: dict):
        content.append(node['content'])
        if node['children']:
            for child in node['children']:
                load_recursive(child)

    for elem in book_data['data']:
        load_recursive(elem)

    return content


if __name__ == '__main__':
    load_dotenv()
    coarse_tagging_config = tagging_config['coarse']
    fine_tagging_config = tagging_config['fine']

    tagger = LocalModelTaggingPipeline(**coarse_tagging_config['local_model'])
    # tagger = GoogleNLPTaggingPipeline(**coarse_tagging_config['google_nlp'])

    for book_name in os.listdir('data/extracted_books'):
        if not os.path.exists(f'data/tags/{book_name}'):
            print(f'Loading book : {book_name.replace(".json", "")}')
            with open(f'data/extracted_books/{book_name}') as f:
                book_data = json.load(f)
            raw_content = load_book_raw_content(book_data)
            raw_tags, text_parts = tagger.tag(raw_content)
            grouped_tags, unique_entity_groups = group_tags(raw_tags=raw_tags)

            result = {
                "text_parts": text_parts,
                "tags": grouped_tags
            }

            if not os.path.exists('data/tags'):
                os.makedirs('data/tags')

            with open(f'data/tags/{book_name}', 'w') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

    with open("data/tags/1-Maia - Riley, Lucinda.json", 'r') as f:
        data = json.load(f)

    grouped_tags = group_tags_by_entity_names(data['tags'])
    filter_classes = [globals()[filter['class']]
                      for filter in tagging_config['filters']]

    for c, config in zip(filter_classes, [checker['config'] for checker in tagging_config['filters']]):
        grouped_tags = c(grouped_tags, **config).filter()

    for k, v in grouped_tags.items():
        print(k, '\t', v)
    exit()

    # fine tagging
    book_store = BookStore(
        bookstore_config['weaviate_connection'],
        bookstore_config['chunking']['sizes'],
        bookstore_config['chunking']['text_splitter'],
        bookstore_config['embedding']
    )

    # globals()[fine_tagging_config['class']]
    fine_tags = OpenAIFineTagger(
        grouped_tags=grouped_tags,
        book_id='86b2e1851765c25637edad76b18ffbf8bdefe36113ac80bbb11ff9d8df616b3c',
        config=fine_tagging_config['config'],
        book_store=book_store
    ).fine_tag()

    if not os.path.exists('data/fine_tags'):
        os.makedirs('data/fine_tags')

    with open("data/fine_tags/1-Maia - Riley, Lucinda.json", 'w') as f:
        json.dump(fine_tags, f, indent=4, ensure_ascii=False)
