from datetime import time

from flask.json.provider import DefaultJSONProvider


class JSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, time):
            return None
        return super().default(obj)
