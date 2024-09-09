import os
from dramatiq.brokers.redis import RedisBroker
from dotenv import load_dotenv

load_dotenv()

broker = RedisBroker(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
