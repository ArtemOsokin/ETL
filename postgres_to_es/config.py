import os
import logging
import uuid
from dataclasses import dataclass

tables = ['genre',
          'person',
          'filmwork',
          'all_tables']

ELASTIC_URL = os.environ.get('ES_URL')
Redis_host = os.environ.get('REDIS_HOST')
delay = 1
batch_size = 100
logger = logging.getLogger()

dsl = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
    'options': '-c search_path=content'
}


@dataclass
class ESMovie:
    id: uuid
    title: str
    rating: float
    type: str
    description: str
    genre: list
    directors_names: list
    actors_names: list
    writers_names: list
    directors: list
    actors: list
    writers: list


