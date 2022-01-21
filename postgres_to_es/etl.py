import json
import logging
import time
from urllib.parse import urljoin

import backoff
import psycopg2
import requests
from psycopg2.extensions import connection as _connection
from psycopg2.extras import RealDictCursor
from redis import Redis

import config
from config_sql import *
from state_storage import RedisStorage

logging.basicConfig(level=logging.DEBUG)


class ETL:
    def __init__(self, conn: _connection, storage: RedisStorage):
        self.conn = conn
        self.storage = storage
        self.urls = config.ELASTIC_URL
        self.batch_size = 100

    def extract(self, state_tab: str):
        up = self.storage.retrieve_state()
        if not up:
            up = 'make_date(1700, 01, 01)'
        else:
            up = 'make_date(' + up[0:4] + ',' + up[5:7] + ',' + up[8:10] + ')'
        curr = self.conn.cursor()
        if state_tab == 'genre':
            curr.execute(get_update_genres(up))
        if state_tab == 'person':
            curr.execute(get_update_persons(up))
        if state_tab == 'filmwork':
            curr.execute(get_update_filmwork(up))
        data = curr.fetchall()
        idx_l = []
        for row in data:
            idx_l.append("'" + row['id'] + "'")
        idx = ', '.join(idx_l)
        if state_tab != 'filmwork':
            if state_tab == 'genre':
                curr.execute(get_update_genre_filmwork_idx(idx))
            if state_tab == 'person':
                curr.execute(get_update_person_filmwork_idx(idx))
            data = curr.fetchall()
            idx_l = []
            for row in data:
                idx_l.append("'" + row['id'] + "'")
            idx = ', '.join(idx_l)
        curr.execute(get_update_film_work_by_idx(idx))
        while data:
            data = curr.fetchmany(self.batch_size)
            yield data
            if not data:
                curr.close()
                break

    def transform(self, data: list):
        for row in data:
            glist, dlist, alist, wlist = [], [], [], []
            if row['genres']:
                for r in row['genres']:
                    glist.append(r['name'])
            if row['directors']:
                for r in row['directors']:
                    dlist.append(r['name'])
            if row['actors']:
                for r in row['actors']:
                    alist.append(r['name'])
            if row['writers']:
                for r in row['writers']:
                    wlist.append(r['name'])
            temp = config.ESMovie(
                id=row['fw_id'],
                title=row['title'],
                description=row['description'],
                rating=row['rating'],
                type=row['type'],
                genre=glist,
                directors=row['directors'],
                actors=row['actors'],
                writers=row['writers'],
                directors_names=dlist,
                actors_names=alist,
                writers_names=wlist
            )
            self.storage.save_state(row['updated_at'])
            yield temp

    def get_es_bulk_query(self, rows: list):
        prepared_query = []
        for row in rows:
            temp_json = {}
            temp_json['id'] = row.id
            temp_json['title'] = row.title
            temp_json['rating'] = row.rating
            temp_json['type'] = row.type
            temp_json['description'] = row.description
            temp_json['directors_names'] = row.directors_names
            temp_json['actors_names'] = row.actors_names
            temp_json['writers_names'] = row.writers_names
            temp_json['directors'] = row.directors
            temp_json['actors'] = row.actors
            temp_json['writers'] = row.writers
            prepared_query.extend([
                json.dumps({'index': {'_index': 'movies', '_id': row.id}}),
                json.dumps(temp_json)
            ])
        return prepared_query

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.ConnectionError,
                           requests.exceptions.Timeout))
    def load(self, prepared_query):
        str_query = '\n'.join(prepared_query) + '\n'
        response = requests.post(
            urljoin(self.urls, '_bulk'),
            data=str_query,
            headers={'Content-Type': 'application/x-ndjson'}
        )
        json_response = json.loads(response.content.decode())
        for item in json_response['items']:
            error_message = item['index'].get('error')
            if error_message:
                logging.error(error_message)
        pass


if __name__ == "__main__":
    with psycopg2.connect(**config.dsl,
                          cursor_factory=RealDictCursor
                          ) as pg_conn:
        try:
            logging.debug(f"Database GO")
            redis_adapter = Redis(host='redis')
            storage = RedisStorage(redis_adapter=redis_adapter)
            etl = ETL(conn=pg_conn, storage=storage)
            while True:
                for tab in config.tables:
                    index_film_data = []
                    for e in etl.extract(tab):
                        for t in etl.transform(e):
                            index_film_data.append(t)
                    etl.load(etl.get_es_bulk_query(index_film_data))
                time.sleep(1)

        except psycopg2.DatabaseError as error:
            logging.debug(f"Database error {error}")
