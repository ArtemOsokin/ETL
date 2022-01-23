import abc
import json

from redis import Redis

from config import logger
from utils import EnhancedJSONEncoder


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""
        pass


class StateStorage(BaseStorage):

    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""

        self.redis_adapter.set(
            'start_from_ts',
            json.dumps(
                state,
                cls=EnhancedJSONEncoder
            )
        )

    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""

        raw_data = self.redis_adapter.get('start_from_ts')
        if raw_data is None:
            logger.info('Continue with the in-memory state since no state file was provided.')
            return {}
        return json.loads(raw_data)
