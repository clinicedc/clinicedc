from __future__ import annotations

import os
from datetime import datetime


class MarkdownWriter:
    def __init__(self, path: str | None = None, overwrite: bool | None = None):
        self.path = self.get_path(path=path, overwrite=overwrite)

    @staticmethod
    def get_path(path: str | None = None, overwrite: bool | None = None) -> str:
        if not path:
            timestamp = datetime.today().strftime("%Y%m%d%H%M")
            path = f"forms_{timestamp}.md"
        if os.path.exists(path):
            if overwrite:
                os.remove(path)
            else:
                raise FileExistsError(f"File exists. Got '{path}'")
        return path

    @staticmethod
    def to_markdown(markdown: str = None) -> str:
        """Returns the markdown as a text string."""
        return "\n".join(markdown)

    def to_file(
        self,
        markdown: str = None,
        pad: int | None = None,
        append: bool | None = None,
        prepend: bool | None = None,
    ) -> None:
        markdown = self.to_markdown(markdown=markdown)
        if pad:
            markdown = markdown + ("\n" * pad)
        if append:
            self._append(markdown)
        elif prepend:
            self._prepend(markdown)
        else:
            self._write(markdown)

    def _write(self, markdown: str = None, mode: str | None = None) -> None:
        mode = mode or "w"
        with open(self.path, mode) as f:
            f.write(markdown)

    def _append(self, markdown) -> None:
        mode = "a"
        self._write(markdown=markdown, mode=mode)

    def _prepend(self, markdown=None) -> None:
        mode = "r+"
        with open(self.path, mode) as f:
            content = f.read()
            f.seek(0, 0)
            f.write(markdown + "\n" + content)
