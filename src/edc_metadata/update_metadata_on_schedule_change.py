import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style

style = color_style()


class UpdateMetadataError(Exception):
    pass


class UpdateMetadataOnScheduleChange:
    def __init__(self, field=None, old_name=None, new_name=None, dry_run=None):
        self.fieldname = field
        self.new_value = new_name
        self.old_value = old_name
        self.dry_run = dry_run
        self.update()

    def update(self):
        sys.stdout.write(style.SUCCESS("\n\nUpdate metadata.\n"))
        sys.stdout.write(style.SUCCESS(f"Field is '{self.fieldname}'.\n"))
        sys.stdout.write(
            style.SUCCESS(
                f"Old value='{self.old_value}', New value='{self.new_value}'.\n"
            )
        )
        if self.dry_run:
            sys.stdout.write(
                style.WARNING("This is a dry run. No records will be updated. \n")
            )
            sys.stdout.write(
                "These models need to updated with the new "
                f"value for field '{self.fieldname}'.\n"
                f"Old value='{self.old_value}', New value='{self.new_value}'.\n"
            )
            for name, model_cls in self.models.items():
                count = model_cls.objects.filter(
                    **{self.fieldname: self.old_value}
                ).count()
                sys.stdout.write(
                    f"{model_cls._meta.label_lower}. {count} records found.\n"
                )
            sys.stdout.write(
                style.ERROR(
                    "No records have been updated. \n"
                    "Set --dry-run=False to update.\n"
                )
            )
        else:
            sys.stdout.write(style.SUCCESS("Updating... \n"))
            for name, model_cls in self.models.items():
                sys.stdout.write(f"Updating {name} ...\r")
                updated = model_cls.objects.filter(
                    **{self.fieldname: self.old_value}
                ).update(**{self.fieldname: self.new_value})
                sys.stdout.write(f"Updated {name}. {updated} records.     \n")
            sys.stdout.write(style.SUCCESS("Done. \n"))

    @property
    def models(self):
        """Returns a dictionary of {name: model_cls} for models
        that have the field.
        """
        models = {}
        for model in django_apps.get_models():
            if [f.name for f in model._meta.get_fields() if f.name == self.fieldname]:
                models.update({model._meta.label_lower: model})
        return models
