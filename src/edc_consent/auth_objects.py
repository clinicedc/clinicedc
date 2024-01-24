from .exceptions import SiteConsentError
from .site_consents import site_consents

navbar_codenames = ["edc_consent.nav_consent"]

navbar_tuples = []
for codename in navbar_codenames:
    navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))

consent_codenames = []
try:
    cdefs = site_consents.get_consent_definitions()
except SiteConsentError:
    site_consents.autodiscover()
    try:
        cdefs = site_consents.get_consent_definitions()
    except SiteConsentError:
        pass
    else:
        models = [cdef.model for cdef in cdefs]

        # TODO: handle reconsent model in auth, should come from
        #  get_consent_definitions.
        # if get_reconsent_model_name():
        #     models.append(get_reconsent_model_name())
        models = list(set(models))
        for model in models:
            for action in ["view_", "add_", "change_", "delete_", "view_historical"]:
                consent_codenames.append(f".{action}".join(model.split(".")))


consent_codenames.extend(navbar_codenames)
consent_codenames.sort()
