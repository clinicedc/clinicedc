from django.core.checks import Error, register

from edc_sites.site import SitesCheckError, sites


@register()
def sites_check(app_configs, **kwargs):  # noqa
    errors = []
    try:
        sites.check()
    except SitesCheckError as e:
        errors.append(
            Error(
                e,
                hint="Sites model is out-of-sync with registry.",
                obj=sites,
                id="edc_sites.E001",
            )
        )
    return errors
