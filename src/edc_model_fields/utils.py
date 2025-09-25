from __future__ import annotations

from collections.abc import Generator


class ChoicesError(Exception):
    pass


class Choices:
    STORE = 0
    DISPLAY = 1

    def __init__(
        self,
        *args: tuple[str, str] | tuple[str, str, str | int],
        fillmeta: bool | None = None,
    ):
        meta_seen = []
        self.choices = []
        for index, arg in enumerate(args):
            store, display, meta = None, None, None
            try:
                store, display, meta = arg
            except ValueError:
                store, display = arg
            if fillmeta:
                meta = str(index + 1) if meta is None else str(meta)
                if meta not in meta_seen:
                    meta_seen.append(meta)
                else:
                    raise ChoicesError(
                        f"Meta values will not be unique. Got ({store}, {display}, {meta}). "
                        f"You may need to declare all meta values explicitly. See {args}."
                    )
            choice = (str(store), str(display), meta)
            self.choices.append(choice)
        self.choices: tuple[tuple[str, str, str], ...] = tuple(self.choices)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.choices})"

    def __str__(self) -> str:
        return str(self.choices)

    def __call__(self, *args, **kwargs) -> tuple[tuple[str, str], ...]:  # noqa: ARG002
        return tuple((c[self.STORE], c[self.DISPLAY]) for c in self.choices)

    def __iter__(self) -> Generator[tuple[str, str, str]]:
        yield from self.choices
