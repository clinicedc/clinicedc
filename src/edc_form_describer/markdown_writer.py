from __future__ import annotations

from pathlib import Path

from django.utils import timezone


class MarkdownWriter:
    """Render a list of markdown lines to a string or a file.

    The constructor is side-effect free: it stores the target `path` and the
    `overwrite` flag but does not touch the filesystem. Path resolution and
    the existence check happen in `to_file`, so callers that only need
    `to_markdown()` never risk a `FileExistsError`.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        overwrite: bool | None = None,
    ):
        self.path = path
        self.overwrite = bool(overwrite)

    def _resolve_path(self) -> Path:
        if self.path:
            return Path(self.path)
        timestamp = timezone.now().strftime("%Y%m%d%H%M")
        return Path(f"forms_{timestamp}.md")

    @staticmethod
    def to_markdown(markdown: list[str]) -> str:
        """Return the markdown as a single text string."""
        return "\n".join(markdown)

    def to_file(self, markdown: list[str], pad: int | None = None) -> Path:
        """Write `markdown` to the resolved path and return that path.

        Raises FileExistsError if the target exists and `overwrite` is falsy.
        """
        path = self._resolve_path()
        if path.exists() and not self.overwrite:
            raise FileExistsError(f"File exists. Got '{path}'")
        text = self.to_markdown(markdown=markdown)
        if pad:
            text += "\n" * pad
        path.write_text(text)
        return path
