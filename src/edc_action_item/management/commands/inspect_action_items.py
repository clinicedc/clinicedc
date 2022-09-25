import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from edc_action_item.models import ActionItem
from edc_action_item.site_action_items import site_action_items


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry-run",
            default=False,
            help="dry run",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry-run"]
        if self.dry_run:
            sys.stdout.write(self.style.NOTICE("\nDry run. No changes will be made.\n"))

        actions = []
        for action in site_action_items.registry.values():
            if action.related_reference_fk_attr:
                actions.append(action)

        print("Ready to inspect actions with a `related_reference_fk_attr`")
        names = [a.name for a in actions]
        print("Inspecting action types:")
        for name in names:
            print(f"  * {name}")

        opts = dict(
            related_action_item__isnull=True,
            action_type__name__in=[a.name for a in actions],
        )

        qs = ActionItem.objects.filter(**opts).order_by("subject_identifier", "created")
        print(f"Found {qs.count()} action_items with missing `related_action_item`.")
        self.inspect_action_items(**opts)
        print("Done.")

    def inspect_action_items(self, **opts):
        for action_item in ActionItem.objects.filter(**opts).order_by(
            "subject_identifier", "created"
        ):
            print(
                action_item,
                action_item.action_cls.related_reference_fk_attr,
                action_item.parent_action_item,
            )
            model_cls = django_apps.get_model(action_item.action_cls.get_reference_model())
            try:
                obj = model_cls.objects.get(action_identifier=action_item.action_identifier)
            except ObjectDoesNotExist:
                print("  skipping")
            else:
                related_obj = getattr(obj, action_item.action_cls.related_reference_fk_attr)
                if not self.dry_run:
                    related_obj.save()
                else:
                    print("  not saving")
                related_action_item = ActionItem.objects.get(
                    action_identifier=related_obj.action_identifier
                )
                action_item.related_action_item = related_action_item
                if not self.dry_run:
                    action_item.save()
                else:
                    print("  not saving")
                print(f"  - updated, set related_action_item={related_action_item}")
            if not self.dry_run:
                model_cls.save()
            else:
                print("  not saving")
            print("******************************************************")
