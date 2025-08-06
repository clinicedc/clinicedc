from typing import Optional


class AliquotIdentifierLengthError(Exception):
    pass


class AliquotIdentifierCountError(Exception):
    pass


class AliquotIdentifier:
    count_padding: int = 2
    identifier_length: int = 18
    primary_aliquot_segment: str = "0000"
    template: str = "{identifier_prefix}{parent_segment}{numeric_code}{count}"

    def __init__(
        self,
        identifier_prefix: Optional[str] = None,
        parent_segment: Optional[str] = None,
        numeric_code: Optional[str] = None,
        count: Optional[int] = None,
    ):
        """
        A class to generate aliquot identifiers:

        Keyword args:
            * identifier_prefix: a prefix as instance of Prefix
            * numeric_code: aliquot type numeric code (2 digits segment)
            * count: sequence in aliquoting history relative to primary. (01 for primary)
        """
        self.count: Optional[int] = count
        self.identifier_prefix: str = identifier_prefix or ""
        self.is_primary: bool = True
        self.numeric_code: str = numeric_code or ""
        self.parent_segment: str = parent_segment or ""
        if not self.identifier_length:
            raise AliquotIdentifierLengthError(
                f"Invalid length. Got {self.identifier_length}."
            )
        if self.parent_segment:
            self.is_primary = False
            if not self.count or self.count <= 1:
                raise AliquotIdentifierCountError(
                    "Unknown aliquot number/count. Expected a number "
                    f"greater than 1. Got {self.count}."
                )
        else:
            self.parent_segment = self.primary_aliquot_segment
            self.count = 1
        self.identifier: str = self.template.format(**self.options)
        if len(self.identifier) != self.identifier_length:
            raise AliquotIdentifierLengthError(
                f"Invalid length. Expected {self.identifier_length}. "
                f"Got len({self.identifier})=={len(self.identifier)}."
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.identifier_length})"

    def __str__(self):
        return self.identifier

    @property
    def options(self) -> dict:
        return dict(
            identifier_prefix=self.identifier_prefix,
            parent_segment=self.parent_segment,
            numeric_code=self.numeric_code,
            count=str(self.count).zfill(self.count_padding or 0),
        )
