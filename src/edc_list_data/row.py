class Row:
    def __init__(self, seq: tuple[str, str], extra: str | None = None):
        self.data = seq
        self.extra = extra
