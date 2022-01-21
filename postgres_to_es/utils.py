import dataclasses
import datetime
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

        return super().default(o)
