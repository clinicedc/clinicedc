from __future__ import annotations

from dataclasses import dataclass, field


class AlreadyRegistered(Exception):
    pass


class InvalidDashboardUrlName(Exception):
    pass


@dataclass
class UrlNames:
    registry: dict[str, str] = field(default_factory=dict)

    def register(
        self, name: str = None, url: str = None, namespace: str | None = None
    ) -> None:
        name = name or url
        complete_url = f"{namespace}:{url}" if namespace else url
        if name in self.registry:
            raise AlreadyRegistered(f"Url already registered. Got {name}.")
        self.registry.update({name: complete_url})

    def register_from_dict(self, **urldata: str) -> None:
        for name, complete_url in urldata.items():
            try:
                namespace, url = complete_url.split(":")
            except ValueError:
                namespace, url = complete_url, None
            self.register(name=name, url=url, namespace=namespace)

    def all(self) -> dict[str, str]:
        return self.registry

    def get(self, name: str) -> str:
        if name not in self.registry:
            raise InvalidDashboardUrlName(
                f"Invalid dashboard url name. Expected one of {self.registry.keys()}. "
                f"Got '{name}'."
            )
        return self.registry.get(name)

    def get_or_raise(self, name: str) -> str:
        return self.get(name)


url_names = UrlNames()
