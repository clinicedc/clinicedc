from typing import Protocol


class AliquotTypeStub(Protocol):
    derivatives: list
    name: str
    alpha_code: str
    numeric_code: str

    def add_derivatives(self: "AliquotTypeStub") -> None:
        ...
