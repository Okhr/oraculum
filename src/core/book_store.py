import os
from dotenv import load_dotenv
from openai import OpenAI
import weaviate
import weaviate.classes.config as wc

from src.config import book_store as bookstore_config


class BookStore:
    def __init__(self, weaviate_connection_dict: dict[str, str | int | bool], chunk_sizes: list[tuple[int, int]], text_splitter_params: dict, embedding_params: dict) -> None:
        self.weaviate_connection_dict = weaviate_connection_dict
        self.chunk_sizes = chunk_sizes
        self.text_splitters = [
            text_splitter_params['class'](chunk_size=chunk_size[0], chunk_overlap=chunk_size[1], **text_splitter_params['parameters']) for chunk_size in self.chunk_sizes
        ]

        if embedding_params['provider'] == 'openai':
            self.embedding_client = OpenAI(
                api_key=os.environ['OPENAI_API_KEY']
            )
            self.embedding_parameters = {
                'model': embedding_params['model'],
                'dimensions': embedding_params['dimensions']
            }
        else:
            raise ValueError(
                f'Unknown embbeding provider : {embedding_params["provider"]}'
            )

        # checking db collections state
        with weaviate.connect_to_custom(**self.weaviate_connection_dict) as client:
            if not 'Book_metadata' in client.collections.list_all().keys():
                client.collections.create(
                    name='Book_metadata',
                    properties=[
                        wc.Property(name='title',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='language',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='creator',
                                    data_type=wc.DataType.TEXT),
                    ]
                )
            if not 'Book_parts' in client.collections.list_all().keys():
                client.collections.create(
                    name='Book_parts',
                    properties=[
                        wc.Property(name='book_id',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='parent_id',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='identifier',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='play_order',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='label',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='content_path',
                                    data_type=wc.DataType.TEXT),
                        wc.Property(name='content_id',
                                    data_type=wc.DataType.TEXT)
                    ]
                )
            for chunk_size in self.chunk_sizes:
                if not f'Chunks_{chunk_size[0]}_{chunk_size[1]}' in client.collections.list_all().keys():
                    client.collections.create(
                        name=f'Chunks_{chunk_size[0]}_{chunk_size[1]}',
                        properties=[
                            wc.Property(name='book_id',
                                        data_type=wc.DataType.TEXT),
                            wc.Property(name='parent_id',
                                        data_type=wc.DataType.TEXT),
                            wc.Property(name='chunk_number',
                                        data_type=wc.DataType.NUMBER),
                            wc.Property(name='content',
                                        data_type=wc.DataType.TEXT),
                        ]
                    )

    def _embedd_text_chunks(self, text_chunks: list[str]) -> list[list[float]]:
        response = self.embedding_client.embeddings.create(
            input=text_chunks,
            **self.embedding_parameters
        )

        return [list(elem.embedding) for elem in response.data]

    def insert_book(self, book_data: dict):
        metadata = book_data['metadata']
        content = book_data['data']


if __name__ == '__main__':
    load_dotenv()
    book_store = BookStore(
        bookstore_config['weaviate_connection'],
        bookstore_config['chunking']['sizes'],
        bookstore_config['chunking']['text_splitter'],
        bookstore_config['embedding']
    )
    book_store.list_collections()
