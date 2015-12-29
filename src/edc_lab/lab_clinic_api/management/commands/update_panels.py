import logging
from django.core.management.base import BaseCommand
from lis.exim.lab_import_lis.classes import ConvertLisAttr
from lis.specimen.lab_panel.models import Panel as LisPanel
from ...models import Panel as EdcPanel

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Command(BaseCommand):

    args = ()
    help = 'Updates panels in use from the Lis.'

    def handle(self, *args, **options):
        convert_lis_attr = ConvertLisAttr()
        self.db = 'lab_api'
        local_panel_names = [panel.name for panel in EdcPanel.objects.all().order_by('name')]
        count = LisPanel.objects.using(self.db).filter(name__in=local_panel_names).count()
        for lis_panel in LisPanel.objects.using(self.db).filter(name__in=local_panel_names).order_by('name'):
            panel, created = convert_lis_attr.panel(lis_panel)
            action = 'Adding'
            if not created:
                action = 'Updating'
            print '{action} {panel}'.format(action=action, panel=panel)
#        lis = [panel.name for panel in LisPanel.objects.using(self.db).all().order_by('name')]
#        diff_set = set(local_panel_names).difference(set(lis))
#        if diff_set:
#            print 'Warning: found {0} in local but not lis.'.format(', '.join(diff_set))
#        diff_set = set(lis).difference(set(local_panel_names))
#        if diff_set:
#            print 'Warning: found {0} in lis but not local.'.format(', '.join(diff_set))
        print 'Done updating {new_count} / {count} panels on Lis connection {db}.'.format(count=count,
                                                                                               new_count=EdcPanel.objects.all().count(),
                                                                                               db=self.db)
