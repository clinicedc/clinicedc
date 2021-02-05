class AlreadyRegistered(Exception):
    pass


class InvalidUrlName(Exception):
    pass


class UrlNames:
    def __init__(self):
        self.registry = {}

    def __call__(self):
        return self.registry

    def __str__(self):
        return self.registry

    def register(self, name=None, url=None, namespace=None):
        name = name or url
        complete_url = f"{namespace}:{url}" if namespace else url
        if name in self.registry:
            raise AlreadyRegistered(f"Url already registered. Got {name}.")
        self.registry.update({name: complete_url})

    def register_from_dict(self, **urldata):
        for name, complete_url in urldata.items():
            try:
                namespace, url = complete_url.split(":")
            except ValueError:
                namespace, url = complete_url, None
            self.register(name=name, url=url, namespace=namespace)

    def get(self, name):
        if name not in self.registry:
            raise InvalidUrlName(
                "Invalid url name. Expected one of " f"{self.registry.keys()}. Got '{name}'."
            )
        return self.registry.get(name)


url_names = UrlNames()
