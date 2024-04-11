from abc import ABC, abstractmethod
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pprint import pp
import re
import statistics
from dotenv import load_dotenv
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from google.cloud import language_v2

from src.core.utils import BoundedTokenBucket
from src.config import core as core_config


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
    coarse_tagging_config = core_config['tagging']['coarse']

    '''
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
    '''

    with open('data/tags/Sorceleur5-local.json', 'r') as f:
        data = json.load(f)

    group_tags_by_entity_names(data['tags'])
