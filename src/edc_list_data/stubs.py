from typing import Protocol

from edc_model.stubs import ModelMetaStub


class ListModelMixinStub(Protocol):
    name: str
    display_name: str
    _meta: ModelMetaStub
