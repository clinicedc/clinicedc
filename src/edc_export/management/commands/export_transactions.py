from django.core.management.base import BaseCommand, CommandError

from ...helpers import ExportModelHelper
from ...models import ExportPlan


class Command(BaseCommand):

    args = '<app_label>.<model_name>'
    help = 'Export transactions for a given app_label.modelname.'
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        try:
            app_label, model_name = args[0].split('.')
        except IndexError:
            raise CommandError(
                'Usage: export_transactions app_label.modelname, e.g. '
                'export_transactions bcpp_subject.subjectreferral')
        export_plan = ExportPlan.objects.get(
            app_label=app_label, object_name=model_name)
        export_model_helper = ExportModelHelper(
            export_plan, app_label, model_name, exception_cls=CommandError)
        exit_status = export_model_helper.export()
        print exit_status
        self.stdout.write(exit_status[1])
