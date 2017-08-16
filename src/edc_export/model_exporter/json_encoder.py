import json

from datetime import datetime
from edc_base.model_mixins import BaseUuidModel
from uuid import UUID


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, UUID):
            return str(o)
        elif isinstance(o, BaseUuidModel):
            return str(o.pk)
        return json.JSONEncoder.default(self, o)
