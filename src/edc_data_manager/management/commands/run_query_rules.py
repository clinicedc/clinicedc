from django.core.management.base import BaseCommand

from edc_data_manager.models import QueryRule
from edc_data_manager.rule import update_query_rules


class Command(BaseCommand):
    help = "Run active data query rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            type=bool,
            help="Verbosity (default=True)",
            default=True,
        )

        parser.add_argument(
            "--title",
            type=str,
            help="Titles. Separate by comma. Default is all rules",
            default="",
        )

    def handle(self, *args, **options):
        opts = dict(verbose=options["verbose"])
        if options["title"]:
            opts.update(
                pks=[
                    o.pk
                    for o in QueryRule.objects.filter(
                        title__in=options["title"].strip().split(",")
                    )
                ]
            )
        update_query_rules(**opts)
