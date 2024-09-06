from huey import RedisHuey
import os

h = RedisHuey('oraculum' ,host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"))