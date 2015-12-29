import logging
from django.core.management.base import BaseCommand
from lis.specimen.lab_aliquot_list.models import AliquotType as LisAliquotType
from ...models import AliquotType

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Command(BaseCommand):

    args = ()
    help = 'Imports aliquot types from the Lis.'

    def handle(self, *args, **options):
        self.db = 'lab_api'
        count = LisAliquotType.objects.using(self.db).all().count()
        for lis_aliquot_type in LisAliquotType.objects.using(self.db).all().order_by('name'):
            aliquot_type, created = AliquotType.objects.get_or_create(name=lis_aliquot_type.name)
            for field in aliquot_type._meta.fields:
                if field.name in [fld.name for fld in lis_aliquot_type._meta.fields if fld.name not in ['id', 'name']]:
                    setattr(aliquot_type, field.name, getattr(lis_aliquot_type, field.name))
            aliquot_type.save()
            action = 'Adding'
            if not created:
                action = 'Updating'
            print '{action} {aliquot_type}'.format(action=action, aliquot_type=aliquot_type)
        lis = [aliquot_type.name for aliquot_type in LisAliquotType.objects.using(self.db).all().order_by('name')]
        local = [aliquot_type.name for aliquot_type in AliquotType.objects.all().order_by('name')]
        diff_set = set(local).difference(set(lis))
        if diff_set:
            print 'Warning: found {0} in local but not lis.'.format(', '.join(diff_set))
        diff_set = set(lis).difference(set(local))
        if diff_set:
            print 'Warning: found {0} in lis but not local.'.format(', '.join(diff_set))
        print 'Done importing {new_count} / {count} aliquot types on Lis connection {db}.'.format(count=count,
                                                                                               new_count=AliquotType.objects.all().count(),
                                                                                               db=self.db)
