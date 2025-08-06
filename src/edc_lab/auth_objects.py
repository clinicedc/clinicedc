from django.apps import apps as django_apps

from edc_lab.utils import get_requisition_model_name

LAB = "LAB"
LAB_VIEW = "LAB_VIEW"
LAB_TECHNICIAN_ROLE = "laboratory_technician"

lab_requisition = []
for action in ["view_", "add_", "change_", "delete_", "view_historical"]:
    lab_requisition.append(f".{action}".join(get_requisition_model_name().split(".")))


lab_codenames = []
for app_config in django_apps.get_app_configs():
    if app_config.name in ["edc_lab"]:
        for model_cls in app_config.get_models():
            for prefix in ["add", "change", "delete", "view"]:
                lab_codenames.append(
                    f"{app_config.name}.{prefix}_{model_cls._meta.model_name}"
                )
lab_codenames.sort()


lab_codenames.extend(lab_requisition)


lab_view_codenames = [
    c for c in lab_codenames if ("view_" in c or "edc_nav" in c or "edc_dashboard" in c)
]
