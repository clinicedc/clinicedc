class Credentials:

    user = None
    passwd = None
    host = None
    port = None
    dbname = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if getattr(self, k) is None:
                setattr(self, k, v)
