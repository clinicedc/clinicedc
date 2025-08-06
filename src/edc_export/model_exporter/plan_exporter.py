from django.apps import apps as django_apps

from .model_exporter import ModelExporter


class PlanExporter:
    notification_cls = None
    model_exporter_cls = ModelExporter
    plan_model = "edc_export.plan"

    def __init__(self, plan_name=None):
        plan_model_cls = django_apps.get_model(self.plan_model)
        self.plan = plan_model_cls.objects.get(name=plan_name)

    def __str__(self):
        return self.plan.name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.plan.name})"

    def export(self):
        model_exporter = self.model_exporter_cls(
            model=self.plan.model,
            field_names=self.plan.field_names,
            exclude_field_names=self.plan.exclude_field_names,
            lookups=self.plan.lookups,
            exclude_m2m=self.plan.exclude_m2m,
            encrypt=self.plan.encrypt,
        )
        path = model_exporter.export()
        if self.plan.notification_name:
            notification = self.notification_cls(
                name=self.plan.notification_name, plan=self.plan, path=path
            )
        notification.notify()
        return path
