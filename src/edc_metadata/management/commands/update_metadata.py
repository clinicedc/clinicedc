import re
import sys

from django.core.management.color import color_style
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError

style = color_style()


class Command(BaseCommand):

    help = "Update metadata for changed visit_schedule/schedule names"
    pattern = "^[0-9a-z_]+$"
    fieldnames = ["visit_schedule_name", "schedule_name"]

    def add_arguments(self, parser):
        parser.add_argument(
            "--field",
            dest="field",
            default=None,
            help=('Field name. Either "visit_schedule_name" or "schedule_name"'),
        )

        parser.add_argument(
            "--old-value",
            dest="old_value",
            default=None,
            help=("Old or existing value"),
        )

        parser.add_argument(
            "--new-value",
            dest="new_value",
            default=None,
            help=("New value to replace the old value"),
        )

        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            default=True,
            help=("Do a dry run. (Default: True)"),
        )

    def handle(self, *args, **options):
        dry_run = False if options.get("dry_run", "") == "False" else True
        self.fieldname = options.get("field")
        self.new_value = options.get("new_value")
        self.old_value = options.get("old_value")

        self.validate_options()

        sys.stdout.write(style.SUCCESS(f"\n\nUpdate metadata.\n"))
        sys.stdout.write(style.SUCCESS(f"Field is '{self.fieldname}'.\n"))
        sys.stdout.write(
            style.SUCCESS(
                f"Old value='{self.old_value}', New value='{self.new_value}'.\n"
            )
        )
        if dry_run:
            sys.stdout.write(
                style.WARNING("This is a dry run. No records will be updated. \n")
            )
            sys.stdout.write(
                f"These models need to updated with the new "
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

    def validate_options(self):
        if self.fieldname not in self.fieldnames:
            raise CommandError(
                f"Invalid attribute name. Expected on of {self.fieldnames}. "
                f"Got '{self.fieldname}'. See --attrname"
            )
        if not re.match(self.pattern, self.old_value or ""):
            raise CommandError(
                f"Invalid old value. Got '{self.old_value}'. See --old_value"
            )
        if not re.match(self.pattern, self.new_value or ""):
            raise CommandError(
                f"Invalid new value. Got '{self.new_value}'. See --new_value"
            )
        if self.old_value == self.new_value:
            raise CommandError(
                f"Nothing to do. Old value and new value are the same. "
                f"Got '{self.old_value}' == '{self.new_value}'"
            )

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
