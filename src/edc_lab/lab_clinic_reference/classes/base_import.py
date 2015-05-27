import logging
from datetime import datetime
from edc.lab.lab_clinic_api.models import TestCode

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class BaseImport(object):
    """Base class for importing grading and reference lists."""
    def __init__(self, db):
        self.db = db

    def get_or_create_list_item(self, test_code, list_obj, lis_list_item_obj, defaults):
        """"Users should override this."""
        return None

    def import_prep(self):
        """"Users should override this."""
        self.lis_list_cls = None
        self.lis_list_item_cls = None
        self.lis_list_key_name = None
        self.list_name = None
        self.local_list_cls = None
        self.local_list_item_cls = None
        self.local_list_item_key_field_names = None
        return None

    def import_list(self):
        self.import_prep()
        count = self.lis_list_item_cls.objects.using(self.db).all().count()
        logger.info('Importing {count} items from list {name} ... '.format(count=count, name=self.list_name))
        # loop thru lis lists as well as all items in the list to update local list and items
        for lis_list in self.lis_list_cls.objects.using(self.db).filter(name=self.list_name):
            local_list, created = self.local_list_cls.objects.get_or_create(name=self.list_name)
            for field in local_list._meta.fields:
                if field.name in [field.name for field in lis_list._meta.fields if field.name != 'id']:
                    setattr(local_list, field.name, getattr(lis_list, field.name))
            local_list.save()
            # now loop thru list items
            for lis_list_item in self.lis_list_item_cls.objects.using(self.db).filter(**{self.lis_list_key_name: lis_list}):
                defaults = {}
                # local test code may not exist or needs to be updated
                test_code, created = TestCode.objects.get_or_create(code=lis_list_item.test_code.code)
                for field in test_code._meta.fields:
                    if field.name in [fld.name for fld in lis_list_item.test_code._meta.fields if fld.name not in ['id', 'code']]:
                        setattr(test_code, field.name, getattr(lis_list_item.test_code, field.name))
                test_code.save()
                # add the updated local test_code instance to defaults
                defaults = {'code': test_code.code}
                # loop thru local list item field names to get attr/value from the lis list item fields
                for field in self.local_list_item_cls._meta.fields:
                    # add any fields not listed in local_list_item_key_field_names to the defaults dictionary
                    if field.name in [fld.name for fld in lis_list_item._meta.fields if fld.name not in self.local_list_item_key_field_names]:
                        defaults[field.name] = getattr(lis_list_item, field.name)
                local_list_item, created = self.get_or_create_list_item(test_code, local_list, lis_list_item, defaults)
                action = 'Adding'
                if not created:
                    # if local list item was not created, it may need to be updated
                    # update with values from the defaults dictionary
                    action = 'Updating'
                    for k, v in defaults.iteritems():
                        setattr(local_list_item, k, v)
                # set the import datetime for reference to this import
                # ..todo:: TODO: would be nice to know, for instances not created, if the instance was changed.
                local_list_item.import_datetime = datetime.today()
                local_list_item.save()
                logger.info('{action} list item for {test_code} {uln} - {lln}'.format(action=action,
                                                                                      test_code=local_list_item.test_code,
                                                                                      uln=local_list_item.uln,
                                                                                      lln=local_list_item.lln))
        logger.info('Done importing {new_count} / {count} items from list {name} on Lis connection {db}.'.format(name=self.list_name,
                                                                                                                 count=count,
                                                                                                                 new_count=self.local_list_item_cls.objects.all().count(),
                                                                                                                 db=self.db))
        return None
