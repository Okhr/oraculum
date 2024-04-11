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
        'filters': [
            {
                'class': 'MajorityClassCountTagFilter', 
                'config': {'min_count': 5}
            },
            {
                'class': 'BlacklistTagFilter', 
                'config': {
                    'blacklist': [
                        r'(L|l|Le|le|La|la)',
                        r'(Ca|ca|ça|Ça)',
                        r'^[a-z][^\s]*$',
                        r'^.$'
                    ]
                }
            }
        ],
        'fine': {}
    },
    'chunking': {
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

frontend = {

}

backend = {

}

weaviate_database = {
    'connection': {
        'http_host': "192.168.1.103",
        'http_port': 8080,
        'http_secure': False,
        'grpc_host': "192.168.1.103",
        'grpc_port': 50051,
        'grpc_secure': False
    },
    'collections': [
        {
            'name': 'Book_metadata',
            'properties': [
                {'name': 'identifier', 'data_type': wc.DataType.TEXT},
                {'name': 'title', 'data_type': wc.DataType.TEXT},
                {'name': 'language', 'data_type': wc.DataType.TEXT},
                {'name': 'creator', 'data_type': wc.DataType.TEXT}
            ]
        },
        {
            'name': 'Text_parts',
            'properties': [
                {'name': 'book_id', 'data_type': wc.DataType.TEXT},
                {'name': 'parent_id', 'data_type': wc.DataType.TEXT},
                {'name': 'identifier', 'data_type': wc.DataType.TEXT},
                {'name': 'play_order', 'data_type': wc.DataType.TEXT},
                {'name': 'label', 'data_type': wc.DataType.TEXT},
                {'name': 'content_path', 'data_type': wc.DataType.TEXT},
                {'name': 'content_id', 'data_type': wc.DataType.TEXT}
            ]
        },
        {
            'name': 'Chunks_250_50',
            'properties': [
                {'name': 'parent_id', 'data_type': wc.DataType.TEXT},
                {'name': 'chunk_number', 'data_type': wc.DataType.NUMBER},
                {'name': 'content', 'data_type': wc.DataType.TEXT}
            ]
        },
        {
            'name': 'Chunks_1000_100',
            'properties': [
                {'name': 'parent_id', 'data_type': wc.DataType.TEXT},
                {'name': 'chunk_number', 'data_type': wc.DataType.NUMBER},
                {'name': 'content', 'data_type': wc.DataType.TEXT}
            ]
        }
    ]
}
