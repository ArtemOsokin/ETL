import os
import logging
import uuid
from dataclasses import dataclass
from typing import List

tables = ['genre',
          'person',
          'filmwork']

ELASTIC_URL = 'http://es:9200'

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
class ESPerson:
    id: str
    full_name: str


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
    directors: List[ESPerson]
    actors: List[ESPerson]
    writers: List[ESPerson]


