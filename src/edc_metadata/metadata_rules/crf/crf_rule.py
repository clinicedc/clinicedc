from typing import Any, Optional

from ...constants import CRF
from ..rule import Rule


class CrfRuleModelConflict(Exception):
    pass


class CrfRule(Rule):
    def __init__(self, target_models: Optional[Any] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.metadata_category = CRF
        self.target_models = target_models

    def run(self, visit: Optional[Any] = None) -> Any:
        if self.source_model in self.target_models:
            raise CrfRuleModelConflict(
                f"Source model cannot be a target model. Got '{self.source_model}' "
                f"is in target models {self.target_models}"
            )
        return super().run(visit=visit)
