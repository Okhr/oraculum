from langchain_text_splitters import RecursiveCharacterTextSplitter
import weaviate.classes.config as wc

core = {
    'parsing': {
        'replace': [
            [r'(\n{3,})', r'\n\n\n'],
            ['’', '\'']
        ],
        'remove_title': True
    },
    'tagging': {
        'coarse': {
            'local_model': {
                'model_name': 'Jean-Baptiste/camembert-ner',
                'splitting_regex': r'(\n)+|[.!?]'
            },
            'google_nlp': {
                'splitting_regex': r'[\n]{3,}'
            }
        },
        'checkers': [
            {
                'class': 'MajorityClassCountTagFilter',
                'config': {'min_count': 5}
            },
            {
                'class': 'BlacklistTagFilter',
                'config': {
                    'blacklist': [
                        r'(^Je$|^Il$)',
                        r'(^L$|^Le$|^La$|^Les$)',
                        r'(^Ca$|^Ça$|^Ce$|^Si$)',
                        r'^[a-z][^\s]*$',
                        r'^.$'
                    ]
                }
            }
        ],
        'fine': {}
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
