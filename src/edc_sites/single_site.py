from __future__ import annotations

from django.conf import settings

from .get_languages_from_settings import get_languages_from_settings


class SiteDomainRequiredError(Exception):
    pass


class SiteCountryRequiredError(Exception):
    pass


class SiteLanguagesError(Exception):
    pass


class SingleSite:
    def __init__(
        self,
        site_id: int,
        name: str,
        *,
        title: str = None,
        country: str = None,
        country_code: str = None,
        language_codes: list[str] | None = None,
        domain: str = None,
        description: str = None,
        fqdn: str = None,
    ):
        if not domain and not fqdn:
            raise ValueError("Require either domain and/or fqdn. Got both as None.")
        self._domain = domain or f"{name}.{fqdn}"

        defined_languages = get_languages_from_settings()
        if language_codes:
            if unknown_language_codes := [
                c for c in language_codes if c not in defined_languages
            ]:
                raise SiteLanguagesError(
                    "Unknown language code(s) associated with site. Language code must be "
                    "defined in settings.LANGUAGES. "
                    f"Expected one of {list(defined_languages.keys())}. "
                    f"Got {unknown_language_codes} for site {site_id}."
                )
            self.languages = {code: defined_languages[code] for code in language_codes}
        else:
            self.languages = defined_languages

        self.site_id = site_id
        self.name = name
        self.title = title or name.title()
        self.country = country or ""
        self.country_code = country_code or ""
        if not country and "multisite" in settings.INSTALLED_APPS:
            raise SiteCountryRequiredError(
                f"Country required when using `multisite`. Got None for `{name}`."
            )
        self.description = description or title

    def __repr__(self):
        return f"{__class__.__name__}(({self.site_id}, {self.domain}, ...))"

    def __str__(self):
        return str(self.domain)

    @property
    def domain(self) -> str:
        """Returns the domain, inserts `uat` if this is a
        UAT server instance.
        """
        as_list = self._domain.split(".")
        if getattr(settings, "EDC_SITES_UAT_DOMAIN", None):
            if "uat" not in as_list:
                as_list.insert(1, "uat")  # after the site name
        else:
            try:
                as_list.remove("uat")
            except ValueError:
                pass
        self._domain = ".".join(as_list)
        return self._domain

    @property
    def site(self) -> tuple:
        return (
            self.site_id,
            self.name,
            self.title,
            self.country,
            self.domain,
        )

    def as_dict(self) -> dict:
        return dict(
            site_id=self.site_id,
            name=self.name,
            title=self.title,
            country=self.country,
            domain=self.domain,
        )

    def save(self, force_insert=False, force_update=False):
        raise NotImplementedError(f"{self.__class__.__name__} cannot be saved.")

    def delete(self):
        raise NotImplementedError("RequestSite cannot be deleted.")
