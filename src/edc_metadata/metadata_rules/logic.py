from typing import Any, Optional

from ..constants import DO_NOTHING, NOT_REQUIRED, REQUIRED


class RuleLogicError(Exception):
    pass


class Logic:

    """A class that serves as a container for the logic attribute
    of a rule, the predicate, and the outcomes (result) of that
    rule; consequence and alternative.
    """

    valid_results = [REQUIRED, NOT_REQUIRED, DO_NOTHING]

    def __init__(
        self,
        predicate: Optional[Any] = None,
        consequence: Optional[str] = None,
        alternative: Optional[str] = None,
        comment: Optional[str] = None,
        **kwargs,  # noqa
    ) -> None:
        if not hasattr(predicate, "__call__"):
            raise RuleLogicError(
                "Predicate must be a callable. For example a "
                'predicate class such as "P" or "PF"'
            )
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative
        self.comment = comment
        for result in [self.consequence, self.alternative]:
            if result not in self.valid_results:
                raise RuleLogicError(
                    f"Invalid result on rule. Expected one of "
                    f"{self.valid_results}. Got {result}."
                )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.predicate}, "
            f"{self.consequence}, {self.alternative})"
        )
