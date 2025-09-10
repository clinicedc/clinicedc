from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field

from .get_languages import get_languages


class SiteDomainRequiredError(Exception):
    pass


class SiteCountryRequiredError(Exception):
    pass


@dataclass(order=True)
class SingleSite:
    site_id: int = field(compare=True)
    name: str
    domain: str
    _: KW_ONLY
    country: str = None
    country_code: str = field(default=None, repr=False)
    language_codes: list[str] = field(default_factory=list, repr=False)
    title: str | None = field(default=None, repr=False)
    languages: dict[str, str] = field(init=False, repr=False)
    description: str = field(init=False)

    def __post_init__(self):
        self.languages = get_languages(self.language_codes, self.site_id)
        self.description = (self.title or self.name).title()

    def __str__(self):
        return str(self.domain)
