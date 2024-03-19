from collections import OrderedDict
import json
import os
import concurrent
from pprint import pp
import re
import statistics
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


class NamedEntityRecognition:
    def __init__(self, model_name: str, entity_groups: list[str]) -> None:
        self.entity_groups = entity_groups
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            model_name)
        self.nlp_pipeline = pipeline(
            'ner',
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy='simple'
        )

    def _preprocess_text(self, text: str | list[str], splitting_regex: str, min_length: int = 0) -> list[str]:
        text_parts = []

        if isinstance(text, str):
            text = [text]

        print('Splitting content')

        for t in text:
            for t_part in re.split(splitting_regex, t):
                t_part = t_part.strip() if t_part else ''
                if len(t_part) > min_length:
                    if len(t_part) > self.tokenizer.max_len_single_sentence:
                        # TODO: if possible, use the number of tokens instead of the number of characters, may be too expensive
                        print(f'Warning : t_part length of {len(t_part)} is longer than max sentence length ({
                              self.tokenizer.max_len_single_sentence}), although it is probably okey since the tokenizer will merge characters')
                    text_parts.append(t_part)
        return text_parts

    def get_raw_tags(self, text: str | list[str]) -> tuple[list[dict], list[str]]:
        text_parts = self._preprocess_text(
            text,
            splitting_regex=r"(\\n)+|[.!?]",
            min_length=10
        )

        tags = []

        print('Extracting tags')
        for i, t_part in enumerate(tqdm(text_parts)):
            for tag in self.nlp_pipeline(t_part):
                if tag['entity_group'] in self.entity_groups:
                    tags.append({
                        'entity_group': tag['entity_group'],
                        'score': tag['score'],
                        'word': tag['word'],
                        'position': (i, tag['start'], tag['end'])
                    })
                    # TODO: Save all t_parts at the begining of the output file and add 'src_text' object to each tag
        return tags, text_parts

    def get_grouped_tags(self, text: str | list[str]) -> tuple[OrderedDict, list[str]]:
        raw_tags, text_parts = self.get_raw_tags(text)

        print('Grouping tags')
        grouped_tags = dict()
        scores = dict()
        for tag in raw_tags:
            entity_group = tag['entity_group']
            word = tag['word']
            if entity_group not in grouped_tags:
                grouped_tags[entity_group] = {}
                scores[entity_group] = {}
            if word not in grouped_tags[entity_group]:
                grouped_tags[entity_group][word] = {'positions': []}
                scores[entity_group][word] = {'scores': []}
            scores[entity_group][word]['scores'].append(
                float(tag['score'])
            )
            grouped_tags[entity_group][word]['positions'].append(tag['position'])

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
        return OrderedDict(sorted(ordered_grouped_tags.items(), key=lambda x: x[0])), text_parts


def load_book_raw_content(book_data: dict) -> list[str]:
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
    ner = NamedEntityRecognition(
        model_name='Jean-Baptiste/camembert-ner',
        entity_groups=['PER', 'LOC', 'MISC', 'ORG']
    )

    # TEST
    with open(f'data/extracted_books/1 - Le Dernier Voeu - Sapkowski, Andrzej.json') as f:
        book_data = json.load(f)
        raw_content = load_book_raw_content(book_data)[:3]
        grouped_tags, text_parts = ner.get_grouped_tags(raw_content)
        result = {
            "text_parts": text_parts,
            "tags": grouped_tags
        }
    with open(f'data/tags/test.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    # END TEST

    '''
    for book_name in os.listdir('data/extracted_books'):
        print(f'Loading book : {book_name.replace(".json", "")}')
        with open(f'data/extracted_books/{book_name}') as f:
            book_data = json.load(f)
        raw_content = load_book_raw_content(book_data)
        grouped_tags = ner.get_grouped_tags(raw_content)

        if not os.path.exists('data/tags'):
            os.makedirs('data/tags')

        with open(f'data/tags/{book_name}', 'w') as f:
            json.dump(grouped_tags, f, ensure_ascii=False, indent=4)

        print()
    '''
