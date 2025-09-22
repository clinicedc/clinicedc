from __future__ import annotations

from dataclasses import dataclass, field

from edc_model_fields.utils import Choices


@dataclass
class Row:
    choice: tuple[str, str] | tuple[str, str, str]
    extra: str | None = None

    name: str = field(init=False)
    display_name: str = field(init=False)
    custom_name: str | None = field(default=None, init=False)

    def __post_init__(self):
        try:
            self.name, self.display_name, self.custom_name = self.choice
        except ValueError:
            self.name, self.display_name = self.choice


@dataclass
class AsListData:
    data: tuple[tuple[str, str, str], ...] | Choices
    rows: list[Row] | None = field(default_factory=list, init=False)

    def __post_init__(self):
        for tpl in self.data:
            self.rows.append(Row(tpl))

    def __call__(self) -> tuple[Row, ...]:
        return tuple(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row.name, row.display_name, row.custom_name
