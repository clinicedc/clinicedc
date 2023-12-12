from django.core.checks import Warning, register

from edc_sites.site import SitesCheckError, sites


@register()
def sites_check(app_configs, **kwargs):  # noqa
    errors = []
    try:
        sites.check()
    except SitesCheckError as e:
        errors.append(
            Warning(
                e,
                hint="History manager is need to detect changes.",
                obj=sites,
                id="edc_sites.E001",
            )
        )
    return errors
