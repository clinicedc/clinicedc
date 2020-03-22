from django.conf import settings


class SiteDomainRequiredError(Exception):
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
        self.site_id = site_id
        self.name = name
        self.title = title or name.title()
        self.country = country or ""
        self.country_code = country_code or ""
        if not country and "multisite" in settings.INSTALLED_APPS:
            raise SiteDomainRequiredError(
                f"Domain required when using `multisite`. Got None for `{name}`."
            )
        if not domain and not fqdn:
            raise ValueError("Require either domain and/or fqdn. Got both as None.")
        self.domain = domain or f"{name}.{fqdn}"
        if getattr(settings, "EDC_SITES_UAT_DOMAIN", None):
            as_list = self.domain.split(".")
            as_list.insert(1, "uat")
            self.domain = ".".join(as_list)
        self.description = description or title

    def __repr__(self):
        return f"{__class__.__name__}((self.site_id, self.domain, ...))"

    def __str__(self):
        return str(self.domain)

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
