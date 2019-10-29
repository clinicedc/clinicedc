import os

from datetime import datetime


class MarkdownWriter:
    def __init__(self, path=None, exists_ok=None):
        self.path = self.get_path(path=path, exists_ok=exists_ok)

    def get_path(self, path=None, exists_ok=None):
        if not path:
            timestamp = datetime.today().strftime("%Y%m%d%H%M")
            path = f"forms_{timestamp}.md"
        if os.path.exists(path):
            if exists_ok:
                os.remove(path)
            else:
                raise FileExistsError(f"File exists. Got '{path}'")
        return path

    def to_markdown(self, markdown=None):
        """Returns the markdown as a text string.
        """
        return "\n".join(markdown)

    def to_file(self, markdown=None, pad=None, append=None, prepend=None):
        markdown = self.to_markdown(markdown=markdown)
        if pad:
            markdown = markdown + ("\n" * pad)
        if append:
            self._append(markdown)
        elif prepend:
            self._prepend(markdown)
        else:
            self._write(markdown)

    def _write(self, markdown=None, mode=None):
        mode = mode or "w"
        with open(self.path, mode) as f:
            f.write(markdown)

    def _append(self, markdown):
        mode = "a"
        self._write(markdown=markdown, mode=mode)

    def _prepend(self, markdown=None):
        mode = "r+"
        with open(self.path, mode) as f:
            content = f.read()
            f.seek(0, 0)
            f.write(markdown + "\n" + content)
