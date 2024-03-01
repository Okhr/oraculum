import json
import os
import ebooklib
from ebooklib import epub
import bs4
from bs4 import BeautifulSoup


def extract_book_metadata(book: ebooklib.epub.EpubBook):
    return {
        'identifier': book.get_metadata('DC', 'identifier'),
        'title': book.get_metadata('DC', 'title')[0][0],
        'language': book.get_metadata('DC', 'language')[0][0],
        'creator': book.get_metadata('DC', 'creator')[0][0]
    }


def extract_structured_toc(book: ebooklib.epub.EpubBook):
    # depth first toc building
    def process_navpoint_recursive(navpoint):
        result = {}
        result['id'] = navpoint['id']
        result['playorder'] = navpoint['playOrder']
        result['label'] = navpoint.navLabel.text.strip()
        content_tuple = navpoint.content['src'].split('#')
        result['content_path'] = content_tuple[0]
        result['content_id'] = content_tuple[1] if len(content_tuple)>1 else None
        #result['content'] = parse_item(book, result['content_path'])

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

    # breadth-first validation and potential merging
    def check_for_duplicate_recursive(node: dict):
        pass

    for part in table_of_content:
        check_for_duplicate_recursive(part)

    return table_of_content


def parse_item(book: ebooklib.epub.EpubBook, item_href: str):
    print(item_href)
    item = book.get_item_with_href(item_href)
    item_body_content = item.get_body_content()
    item_soup = BeautifulSoup(item_body_content, features='lxml')
    item_text = item_soup.html.body.get_text().strip()
    return item_text


if __name__ == '__main__':
    EBOOK_PATH = "data/epubs/Sorceleur - L'Integrale - Andrzej Sapkowski.epub"
    book = epub.read_epub(EBOOK_PATH)

    print(json.dumps(extract_structured_toc(book), indent=4))

    """encode
    documents = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    images = list(book.get_items_of_type(ebooklib.ITEM_IMAGE))
    navigation = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    covers = list(book.get_items_of_type(ebooklib.ITEM_COVER))

    parse_item("Sapkowski, Andrzej - Le Dernier Voeu_split_004.htm")
    """
