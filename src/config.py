from langchain_text_splitters import RecursiveCharacterTextSplitter
import weaviate.classes.config as wc

parsing = {
    'replace': [
        [r'(\n{3,})', r'\n\n\n'],
        ['’', '\'']
    ],
    'remove_title': True
}

tagging = {
    'coarse': {
        'local_model': {
            'model_name': 'Jean-Baptiste/camembert-ner',
            'splitting_regex': r'(\n)+|[.!?]'
        },
        'google_nlp': {
            'splitting_regex': r'[\n]{3,}'
        }
    },
    'filters': [
        {
            'class': 'MajorityClassCountTagFilter',
            'config': {'min_count': 5}
        },
        {
            'class': 'BlacklistTagFilter',
            'config': {
                'blacklist': [
                    r'(^Je$|^Il$)',
                    r'(^Lille$)',
                    r'(^L$|^Le$|^La$|^Les$)',
                    r'(^Ca$|^Ça$|^Ce$|^Ces$|^Si$|^Ses$)',
                    r'^[a-z][^\s]*$',
                    r'^.$'
                ]
            }
        }
    ],
    'fine': {
        'class': 'OpenAIFineTagger',
        'config': {
            'prompt_template': 'I want you to classify a named entity (single word or group of words) into the right category.\nI will give you a list of text chunks (between <CHUNKS> and </CHUNKS>) where the entity appears, a list of category names with their descriptions (between <CATEGORIES> and </CATEGORIES>), and the entity to classify (between <ENTITY> and </ENTITY>).\nYou will only answer using the category name, NOTHING ELSE, you are only allowed to use one of the categories I provided to you.\n\n<CHUNKS>\n{chunks}\n</CHUNKS>\n\n<CATEGORIES>\nPER : a single person\nLOC : a location\nORG : an organization of people\nMISC : everything else\n</CATEGORIES>\n\n<ENTITY>\n{entity}\n</ENTITY>\n\nAnswer with one category name, nothing else',
            'majority_class_threshold': 0.7,
            'number_chunks': 5,
            'chunk_size': (250, 50),
            'vector_db_query': 'person, location, organization, miscellaneous'
        }
    }
}

frontend = {

}

backend = {

}

book_store = {
    'weaviate_connection': {
        'http_host': "192.168.1.103",
        'http_port': 8080,
        'http_secure': False,
        'grpc_host': "192.168.1.103",
        'grpc_port': 50051,
        'grpc_secure': False
    },
    'chunking': {
        'sizes': [
            (250, 50),
            (1000, 100)
        ],
        'text_splitter': {
            'class': RecursiveCharacterTextSplitter,
            'parameters': {
                'separators': ["\n\n\n", "\n\n", "\n", ".", ",", " ", ""],
                'keep_separator': False,
                'length_function': len
            }
        }
    },
    'embedding': {
        'provider': 'openai',
        'model': 'text-embedding-3-small',
        'dimensions': 1536
    }
}
