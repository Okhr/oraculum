import hashlib
import json
import os
from pprint import pp
from dotenv import load_dotenv
from openai import OpenAI
import weaviate
import weaviate.classes.config as wc
import weaviate.classes.query as wq

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
                        wc.Property(name='book_id',
                                    data_type=wc.DataType.TEXT),
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

    def _embed_text_chunks(self, text_chunks: list[str]) -> list[list[float]]:
        response = self.embedding_client.embeddings.create(
            input=text_chunks,
            **self.embedding_parameters
        )

        return [list(elem.embedding) for elem in response.data]

    def insert_book(self, book_data: dict):
        metadata = book_data['metadata']
        content = book_data['data']

        book_id = hashlib.sha256(json.dumps(
            metadata['identifier'], sort_keys=True).encode()).hexdigest()
        print(f'book_id : {book_id}')

        with weaviate.connect_to_custom(**self.weaviate_connection_dict) as client:
            book_metadata_collection = client.collections.get('Book_metadata')
            book_parts_collection = client.collections.get('Book_parts')
            chunk_collections = [client.collections.get(
                f'Chunks_{chunk_size[0]}_{chunk_size[1]}') for chunk_size in self.chunk_sizes]

            with book_metadata_collection.batch.dynamic() as batch:
                book_metadata_obj = {
                    "book_id": book_id,
                    "title": metadata['title'],
                    "language": metadata['language'],
                    "creator": metadata['creator']
                }
                batch.add_object(
                    properties=book_metadata_obj,
                )

            if len(book_metadata_collection.batch.failed_objects) > 0:
                print(f"Failed to import book metadata : {
                      book_metadata_collection.batch.failed_objects}")

            # Iterating over book parts
            def insert_book_part_recursive(book_part: dict, parent_id: str):
                print(f'Inserting : {book_part["label"]}')
                with book_parts_collection.batch.dynamic() as batch:
                    obj = {
                        "book_id": book_id,
                        "parent_id": parent_id,
                        "identifier": book_part['id'],
                        "play_order": str(book_part['playorder']),
                        "label": book_part['label'],
                        "content_path": book_part['content_path'],
                        "content_id": book_part['content_id']
                    }
                    batch.add_object(
                        properties=obj
                    )

                if len(book_parts_collection.batch.failed_objects) > 0:
                    print(f"Failed to import book parts : {
                          book_parts_collection.batch.failed_objects}")

                # splitting content for each chunk size:
                for i in range(len(self.chunk_sizes)):
                    chunk_collection = chunk_collections[i]
                    chunks = self.text_splitters[i].split_text(
                        book_part['content'])
                    if not chunks:
                        chunks = [' ']
                    embeddings = self._embed_text_chunks(chunks)

                    with chunk_collection.batch.dynamic() as batch:
                        for i, chunk in enumerate(chunks):
                            obj = {
                                "book_id": book_id,
                                "parent_id": book_part['id'],
                                "chunk_number": i,
                                "content": chunk
                            }
                            batch.add_object(
                                properties=obj,
                                vector=embeddings[i]
                            )

                    if len(chunk_collection.batch.failed_objects) > 0:
                        print(f"Failed to import {self.chunk_sizes[i]} chunks: {
                              chunk_collection.batch.failed_objects}")

                for child in book_part['children']:
                    insert_book_part_recursive(child, book_part['id'])

            for child in content:
                insert_book_part_recursive(child, '')

    def retrieve_chunks(self, book_id: str, query: str, chunk_size: tuple[int, int], max_retrieved_chunks: int, contains_token: list[str] = None) -> list[tuple[str, float]]:
        if chunk_size not in self.chunk_sizes:
            raise ValueError(f'Chunk size : {chunk_size} is not valid')
        else:
            query_vector = self._embed_text_chunks([query])[0]

            with weaviate.connect_to_custom(**self.weaviate_connection_dict) as client:
                chunk_collection = client.collections.get(
                    f'Chunks_{chunk_size[0]}_{chunk_size[1]}')

                if contains_token is not None:
                    response = chunk_collection.query.near_vector(
                        near_vector=query_vector,
                        limit=max_retrieved_chunks,
                        return_metadata=wq.MetadataQuery(distance=True),
                        filters=wq.Filter.by_property("book_id").equal(book_id) &
                        wq.Filter.by_property(
                            "content").contains_any(contains_token)
                    )
                else:
                    response = chunk_collection.query.near_vector(
                        near_vector=query_vector,
                        limit=max_retrieved_chunks,
                        return_metadata=wq.MetadataQuery(distance=True),
                        filters=wq.Filter.by_property("book_id").equal(book_id)
                    )

                return [(o.properties['content'], o.metadata.distance) for o in reversed(response.objects)]

    def delete(self):
        with weaviate.connect_to_custom(**self.weaviate_connection_dict) as client:
            client.collections.delete_all()


if __name__ == '__main__':
    load_dotenv()
    book_store = BookStore(
        bookstore_config['weaviate_connection'],
        bookstore_config['chunking']['sizes'],
        bookstore_config['chunking']['text_splitter'],
        bookstore_config['embedding']
    )
    book_store.delete()
    with open("data/extracted_books/Sorceleur - L'Integrale - Andrzej Sapkowski.json", 'r') as f:
        data = json.load(f)

    book_store.insert_book(data)

    retrieved_chunks = book_store.retrieve_chunks(
        book_id='55d5d45b5d08076c83c8adf4cbc6ca83857edad9aa8e1972521e99dc2ebb21ec',
        query='person, location, organization, other',
        chunk_size=(250, 50),
        max_retrieved_chunks=10,
        contains_token=['Signe']
    )

    for text, distance in retrieved_chunks:
        print(text)
        print()
        print(distance)
        print('---')
        print()
