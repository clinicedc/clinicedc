from django.core.management.base import BaseCommand

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
            "--rule_ids",
            type=str,
            help="Rule IDs. Separate by comma. Default is all rule IDs",
            default="",
        )

    def handle(self, *args, **options):
        opts = dict(verbose=options["verbose"])
        if options["rule_ids"]:
            opts.update(pks=options["rule_ids"].strip().split(","))
        update_query_rules(**opts)
