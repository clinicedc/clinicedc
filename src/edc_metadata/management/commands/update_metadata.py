import sys

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import color_style
from edc_visit_tracking.models import get_subject_visit_model_cls
from tqdm import tqdm

from edc_metadata import site_metadata_rules

style = color_style()


class Command(BaseCommand):

    help = "Update metadata and run metadatarules"

    def handle(self, *args, **options):
        sys.stdout.write(f"Updating metadata and running metadatarules ...\n")
        source_models = [get_subject_visit_model_cls()._meta.label_lower]
        for app_label, rule_groups_list in site_metadata_rules.rule_groups.items():
            for rule_groups in rule_groups_list:
                source_models.append(rule_groups._meta.source_model)
        source_models = list(set(source_models))
        sys.stdout.write(f"  Found source models: {', '.join(source_models)}.\n")
        for index, source_model in enumerate(source_models):
            sys.stdout.write(f"  {index + 1}. {source_model}\n")

            source_model_cls = django_apps.get_model(source_model)

            total = source_model_cls.objects.all().count()

            sys.stdout.write("    - Updating references ...\n")
            for instance in tqdm(source_model_cls.objects.all(), total=total):
                instance.update_reference_on_save()

            sys.stdout.write("    - Updating metadata ...     \n")
            for instance in tqdm(source_model_cls.objects.all(), total=total):
                try:
                    instance.metadata_create()
                except AttributeError:
                    try:
                        instance.metadata_update()
                    except AttributeError as e:
                        sys.stdout.write(f"      skipping (got {e})     \n")

            sys.stdout.write("    - Running rules ...     \n")
            for instance in tqdm(source_model_cls.objects.all(), total=total):
                if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
                    instance.run_metadata_rules()
        sys.stdout.write("Done.\n")
