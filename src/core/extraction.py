import json
import ebooklib
from ebooklib import epub
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
        result['content_id'] = content_tuple[1] if len(
            content_tuple) > 1 else None
        # result['content'] = parse_item(book, result['content_path'])

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
            'id': [node['id']],
            'playorder': [node['playorder']],
            'label': [node['label']],
            'content_path': node['content_path'],
            'content_id': [node['content_id']],
            'content': parse_item(book, node['content_path']),
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
                        'id': [child['id']],
                        'playorder': [child['playorder']],
                        'label': [child['label']],
                        'content_path': content_path,
                        'content_id': [child['content_id']],
                        'content': parse_item(book, child['content_path']),
                        'children': child['children']
                    }
                    for other_child in node['children']:
                        if other_child['content_path'] == content_path and other_child['id'] != child['id']:
                            merged_child['id'].append(other_child['id'])
                            merged_child['playorder'].append(
                                other_child['playorder'])
                            merged_child['label'].append(other_child['label'])
                            merged_child['content_id'].append(
                                other_child['content_id'])
                            merged_child['children'].extend(
                                other_child['children'])

                    if len(merged_child['id']) > 1 and merged_child['children']:
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


def parse_item(book: ebooklib.epub.EpubBook, item_href: str):
    item = book.get_item_with_href(item_href)
    if item is None:
        raise ValueError(f"No item found for : {item_href}")

    item_body_content = item.get_body_content()
    item_soup = BeautifulSoup(item_body_content, "lxml")

    # finding where the majority of p lie
    p_tags = item_soup.body.find_all('p')
    if not p_tags:
        return ''

    tag_counts = {}
    for p_tag in p_tags:
        parent_tag = p_tag.parent
        if parent_tag:
            tag_counts[parent_tag] = tag_counts.get(parent_tag.name, 0) + 1
    
    print(item_href)

    parent_tag = max(tag_counts, key=tag_counts.get)

    content = []
    for tag in parent_tag.find_all(recursive=False):
        tag_content = tag.get_text().strip()
        tag_content = tag_content.replace('\n', ' ').replace('  ', ' ')
        content.append(tag_content)

    return '\n'.join(content)

def write_extracted_book_data(book: ebooklib.epub.EpubBook, path: str):
    extracted_book = {
        'metadata': extract_book_metadata(book),
        'data': extract_structured_toc(book)
    }

    with open(path, 'w') as f:
        json.dump(extracted_book, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    EBOOK_PATH = "data/epubs/1 - Dune - Frank Herbert.epub"
    book = epub.read_epub(EBOOK_PATH)
    write_extracted_book_data(book, 'data/test.json')
    
    '''
    print(json.dumps(extract_structured_toc(book), indent=4, ensure_ascii=False))
    content = parse_item(
        book, 
        "p2chap7.xhtml"
    )
    print(content)
    print(len(content))
    '''

    """
    documents = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    images = list(book.get_items_of_type(ebooklib.ITEM_IMAGE))
    navigation = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    covers = list(book.get_items_of_type(ebooklib.ITEM_COVER))
    """
