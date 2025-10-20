from __future__ import annotations

from dataclasses import dataclass, field


class AlreadyRegistered(Exception):  # noqa: N818
    pass


class InvalidDashboardUrlName(Exception):  # noqa: N818
    pass


@dataclass
class UrlNames:
    registry: dict[str, str] = field(default_factory=dict)

    def register(
        self,
        key: str,
        namespace: str | None = None,
        url: str | None = None,
        url_with_namespace: str | None = None,
    ) -> None:
        url_with_namespace = url_with_namespace or f"{namespace}:{url}"
        if key in self.registry:
            raise AlreadyRegistered(
                "Url already registered with url_names. "
                f"See {key}:{self.registry[key]}. Got {url_with_namespace}."
            )
        self.registry.update({key: url_with_namespace})

    def register_from_dict(self, **urldata: str) -> None:
        for key, url_with_namespace in urldata.items():
            try:
                namespace, url = url_with_namespace.split(":")
            except ValueError:
                namespace, url = url_with_namespace, None
            self.register(key, namespace, url=url)

    def all(self) -> dict[str, str]:
        return self.registry

    def get(self, key: str) -> str:
        if key not in self.registry:
            raise InvalidDashboardUrlName(
                f"Invalid key for url_names. Expected one of {self.registry.keys()}. "
                f"Got '{key}'."
            )
        return self.registry.get(key)

    def get_or_raise(self, key: str) -> str:
        return self.get(key)


url_names = UrlNames()
