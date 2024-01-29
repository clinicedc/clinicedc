from django.apps import apps as django_apps
from django.core.management.color import color_style

style = color_style()


def update_panels_on_post_migrate(sender, **kwargs):
    from edc_lab.site_labs import site_labs

    site_labs.migrated = True
    if site_labs.loaded:
        site_labs.update_panel_model(panel_model_cls=django_apps.get_model("edc_lab.panel"))
