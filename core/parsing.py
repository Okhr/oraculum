import json
import os
import re
import urllib
import ebooklib
from ebooklib import epub
import bs4
from bs4 import BeautifulSoup


from core.config import parsing as parsing_config


def extract_book_metadata(book: ebooklib.epub.EpubBook) -> dict[str, str | list[str]]:
    """Extract metadata from an EPUB book.

    Parameters
    ----------
    book : ebooklib.epub.EpubBook
        The EPUB book object.

    Returns
    -------
    dict
        Metadata information including 'identifier', 'title', 'language', and 'creator'.
    """

    return {
        'identifier': book.get_metadata('DC', 'identifier'),
        'title': book.get_metadata('DC', 'title')[0][0],
        'language': book.get_metadata('DC', 'language')[0][0],
        'creator': book.get_metadata('DC', 'creator')[0][0]
    }


def extract_structured_toc(book: ebooklib.epub.EpubBook) -> list[dict[str, str | dict]]:
    """Extract the structured table of contents (TOC) from an EPUB book.

    Parameters
    ----------
    book : ebooklib.epub.EpubBook
        The EPUB book object.

    Returns
    -------
    list[dict]
        A list containing dictionaries representing the structured TOC.
    """

    # depth first toc building
    def process_navpoint_recursive(navpoint):
        result = {}
        result['id'] = navpoint['id']
        result['playorder'] = navpoint['playOrder']
        result['label'] = navpoint.navLabel.text.strip()
        content_tuple = navpoint.content['src'].split('#')
        result['content_path'] = urllib.parse.unquote(content_tuple[0])
        result['content_id'] = urllib.parse.unquote(content_tuple[1]) if len(
            content_tuple) > 1 else ''

        children_navpoints = navpoint.find_all('navPoint')
        if len(children_navpoints) > 0:
            result['children'] = [process_navpoint_recursive(
                child) for child in children_navpoints]
        else:
            result['children'] = []

        return result

    navs = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    nav_html = navs[0].content.decode('utf-8')
    nav_soup = BeautifulSoup(nav_html, features="xml")
    navmap = nav_soup.navMap

    table_of_content = []

    for child in navmap.children:
        if child.name == 'navPoint':
            table_of_content.append(process_navpoint_recursive(child))

    # breadth-first validation and potential merging, also fetches content
    def check_for_duplicate_recursive(node: dict):
        returned_node = {
            'id': node['id'],
            'playorder': node['playorder'],
            'label': node['label'],
            'content_path': node['content_path'],
            'content_id': node['content_id'],
            'content': parse_item(book, node['content_path'], node['label']),
            'children': node['children']
        }
        if node['children'] == []:
            return returned_node
        else:
            # Merge children that share the same content_path
            merged_children = []
            content_paths = set()
            for child in node['children']:
                content_path = child['content_path']
                if content_path not in content_paths:
                    # new unseen content_path
                    content_paths.add(content_path)
                    merged_child = {
                        'id': child['id'],
                        'playorder': child['playorder'],
                        'label': child['label'],
                        'content_path': content_path,
                        'content_id': child['content_id'],
                        'content': parse_item(book, child['content_path'], child['label']),
                        'children': child['children']
                    }
                    for other_child in node['children']:
                        if other_child['content_path'] == content_path and other_child['id'] != child['id']:
                            merged_child['id'] += '|' + other_child['id']
                            merged_child['playorder'] += '|' + \
                                other_child['playorder']
                            merged_child['label'] += '|' + other_child['label']
                            merged_child['content_id'] += '|' + \
                                other_child['content_id']
                            merged_child['children'].extend(
                                other_child['children'])

                    if '|' in merged_child['id'] and merged_child['children']:
                        # a merge can't have children
                        raise RuntimeError(
                            f"Merged child {merged_child['id']} has children"
                        )

                    merged_children.append(merged_child)

            if len(merged_children) != len(node['children']):
                returned_node['children'] = merged_children
                return returned_node
            else:
                # recursively merge children
                returned_node['children'] = [check_for_duplicate_recursive(
                    child) for child in returned_node['children']]
                return returned_node

    for i, part in enumerate(table_of_content):
        table_of_content[i] = check_for_duplicate_recursive(part)

    return table_of_content


def parse_item(book: ebooklib.epub.EpubBook, item_href: str, label: str) -> str:
    """Parse content of a specific item within an EPUB book.

    Parameters
    ----------
    book : ebooklib.epub.EpubBook
        The EPUB book object.
    item_href : str
        Href of the item to parse.
    label : str
        Label of the text part

    Returns
    -------
    str
        Parsed content of the item.
    """

    item = book.get_item_with_href(item_href)
    if item is None:
        raise ValueError(f"No item found for : {item_href}")

    item_body_content = item.get_body_content()
    item_soup = BeautifulSoup(item_body_content, "lxml")

    def merge_tag_recursive(elem: bs4.element.Tag | bs4.element.NavigableString):
        if isinstance(elem, bs4.element.NavigableString):
            return elem.get_text(strip=True)
        elif isinstance(elem, bs4.element.Tag):
            # TODO : if a tag contains a succession of spans, merge them without \n first, can be a p, a h1, h2 etc ...
            if elem.name == 'p':
                content = elem.get_text(separator=' ', strip=True)
                return content.replace('\n', ' ').replace('  ', ' ')
            else:
                return '\n'.join([merge_tag_recursive(child) for child in elem.children])
        else:
            raise TypeError('Element is not of type Tag or NavigableString')

    parsed_content = '\n'.join([merge_tag_recursive(child)
                               for child in item_soup.body.children])

    if parsing_config['remove_title']:
        parsed_content = remove_title(parsed_content.strip(), label)

    for replacement in parsing_config['replace']:
        parsed_content = re.sub(replacement[0], replacement[1], parsed_content)

    return parsed_content


def remove_title(text_part: str, title: str) -> str:
    """Remove, if possible, the text contained in the 'title' parameter from the beginning of the text

    Parameters
    ----------
    text_part : str
        The raw text
    title : str
        The portion of text to remove

    Returns
    -------
    str
        Text with title removed
    """
    text_part = text_part.strip()
    title = title.strip()

    while len(title) > 0 and len(text_part) > 0:
        if text_part[0].lower() == title[0].lower():
            text_part = text_part[1:].strip()
            title = title[1:].strip()
        else:
            break

    return text_part


def write_extracted_book_data(book: ebooklib.epub.EpubBook, path: str) -> None:
    """Write extracted metadata and structured TOC of an EPUB book to a JSON file.

    Parameters
    ----------
    book : ebooklib.epub.EpubBook
        The EPUB book object.
    path : str
        The path to write the JSON file.

    Returns
    -------
    None
    """

    extracted_book = {
        'metadata': extract_book_metadata(book),
        'data': extract_structured_toc(book)
    }

    with open(path, 'w') as f:
        json.dump(extracted_book, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    if not os.path.exists('data/extracted_books'):
        os.makedirs('data/extracted_books')
    for file_name in os.listdir('data/epubs'):
        print(f'Extracting {file_name}')
        book = epub.read_epub(f'data/epubs/{file_name}')
        write_extracted_book_data(
            book, f'data/extracted_books/{file_name.replace('.epub', '.json')}'
        )
