import json
import logging
import time
from datetime import datetime
from dataclasses import asdict
from urllib.parse import urljoin

import backoff
import psycopg2
import requests
from psycopg2.extensions import connection as _connection
from psycopg2.extras import RealDictCursor
from redis import Redis

import config
import config_sql
from state_storage import StateStorage

logging.basicConfig(level=logging.DEBUG)


class ETL:
    def __init__(self, conn: _connection, storage: StateStorage):
        self.conn = conn
        self.storage = storage
        self.urls = config.elastic_url

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.ConnectionError,
                           requests.exceptions.Timeout))
    def extract(self, state_tab: str):
        up = self.storage.retrieve_state()
        if not up:
            up = datetime.min.isoformat()
        curr_i = self.conn.cursor()
        curr_all = self.conn.cursor()
        if state_tab == 'all_tables':
            curr_i.execute(config_sql.get_update_film_work_person_genre(up))
        if state_tab == 'filmwork':
            curr_i.execute(config_sql.get_update_filmwork(up))
        if state_tab == 'genre':
            curr_i.execute(config_sql.get_update_genre_filmwork(up))
        if state_tab == 'person':
            curr_i.execute(config_sql.get_update_person_filmwork(up))
        while True:
            data = curr_i.fetchmany(config.batch_size)
            if not data:
                curr_i.close()
                curr_all.close()
                break
            idx = ', '.join("'{}'".format(row['id']) for row in data)
            curr_all.execute(config_sql.get_update_film_work_by_idx(idx))
            yield curr_all.fetchall()

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
                genres=glist,
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
            temp_json = asdict(row)
            prepared_query.extend([
                json.dumps({'index': {
                    '_index': 'movies',
                    '_id': temp_json['id']
                }}),
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


def start(connect):
    try:
        logging.debug("ETL GO")
        redis_adapter = Redis(host=config.redis_host)
        storage = StateStorage(redis_adapter=redis_adapter)
        etl = ETL(conn=connect, storage=storage)
        while True:
            for tab in config.tables:
                for extracted in etl.extract(tab):
                    film_data_to_es = []
                    for transformed in etl.transform(extracted):
                        film_data_to_es.append(transformed)
                    etl.load(etl.get_es_bulk_query(film_data_to_es))
                logging.debug(f"Table {tab} check")
            time.sleep(config.delay)
    except psycopg2.DatabaseError as error:
        logging.error(f"Database error {error}")


if __name__ == "__main__":
    with psycopg2.connect(**config.dsl,
                          cursor_factory=RealDictCursor
                          ) as pg_conn:
        start(pg_conn)
