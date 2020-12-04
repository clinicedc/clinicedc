from django.conf import settings


class SiteDomainRequiredError(Exception):
    pass


class SiteCountryRequiredError(Exception):
    pass


class SingleSite:
    def __init__(
        self,
        site_id,
        name,
        title=None,
        country=None,
        country_code=None,
        domain=None,
        description=None,
        fqdn=None,
    ):
        if not domain and not fqdn:
            raise ValueError("Require either domain and/or fqdn. Got both as None.")
        self._domain = domain or f"{name}.{fqdn}"
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
    def domain(self):
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
    def site(self):
        return (
            self.site_id,
            self.name,
            self.title,
            self.country,
            self.domain,
        )

    def as_dict(self):
        return dict(
            site_id=self.site_id,
            name=self.name,
            title=self.title,
            country=self.country,
            domain=self.domain,
        )

    def save(self, force_insert=False, force_update=False):
        raise NotImplementedError("RequestSite cannot be saved.")

    def delete(self):
        raise NotImplementedError("RequestSite cannot be deleted.")
