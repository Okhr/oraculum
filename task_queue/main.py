import os
from dramatiq.brokers.redis import RedisBroker
from dotenv import load_dotenv
from task_queue.parsing import extract_book_parts_task
from task_queue.entity_extraction import extract_entities_task

load_dotenv()

broker = RedisBroker(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
