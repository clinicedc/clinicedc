from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model

from edc_meta_data.models import CrfEntry


class Permissions(object):

    def __init__(self, group_name, permission_profile, app_label=None,
                 models=None, visit_definition_codes=None, show_messages=False):
        """Add permissions to a group for the models in a
        visit_definition or list of visit_definitions."""
        # TODO: could add a "view" permission here in addition to django's add, change, delete
        #       maybe use it to manpulate the submit row on the change_form.
        self.show_messages = show_messages
        self.set_permission_profile(permission_profile)
        self.set_group(group_name)
        if app_label and visit_definition_codes:
            raise AttributeError(
                'You must specify either a list of visit definition codes '
                'or the app_label with a list of models. List of models may be None.')
        if visit_definition_codes:
            self.set_visit_definitions(visit_definition_codes)
            self.set_content_types_by_visit_definition(visit_definition_codes)
        elif app_label:
            self.set_content_types(app_label, models)
        else:
            raise AttributeError(
                'You must specify either a list of visit definition codes or '
                'the app_label with a list of models. List of models may be None.')

    def update(self):
        """Updates permissions to the group based on the list of content_types
        and the profile.

        Permission instance must already exist in the Permissions model
        (e.g. put in by django on syncdb...)"""
        for content_type in self.get_content_types():
            if 'add' in self.get_permission_profile():
                if not self.get_group().permissions.filter(
                        content_type=content_type, codename__icontains='add' + '_'):
                    # To avoid duplicates
                    permisons = Permission.objects.filter(
                        content_type=content_type, codename__icontains='add' + '_')
                    try:
                        for permision in permisons:
                            if permision:
                                self.get_group().permissions.add(permision)
                    except Permission.DoesNotExist:
                        raise TypeError('Permissions do not exist. Run syncdb')
                    for permision in permisons:
                        if permision:
                            self.message(permision)
            if 'change' in self.get_permission_profile():
                if not self.get_group().permissions.filter(
                        content_type=content_type, codename__icontains='change' + '_'):
                    permisons = Permission.objects.filter(
                        content_type=content_type, codename__icontains='change' + '_')
                    try:
                        for permision in permisons:
                            if permision:
                                self.get_group().permissions.add(permision)
                    except Permission.DoesNotExist:
                        raise TypeError('Permissions do not exist. Run syncdb')
                    for permision in permisons:
                        if permision:
                            self.message(permision)
            if 'delete' in self.get_permission_profile():
                if not self.get_group().permissions.filter(
                        content_type=content_type, codename__icontains='delete' + '_'):
                    permisons = Permission.objects.filter(
                        content_type=content_type, codename__icontains='delete' + '_')
                    try:
                        for permision in permisons:
                            if permision:
                                self.get_group().permissions.add(permision)
                    except Permission.DoesNotExist:
                        raise TypeError('Permissions do not exist. Run syncdb')
                    for permision in permisons:
                        if permision:
                            self.message(permision)

    def replace(self):
        """Replaces permissions to the group by deleting all for this group then calling update."""
        self.clear_permissions_for_group()
        self.update()

    def clear_permissions_for_group(self):
        """"Clears permissions for this group."""
        self.get_group().permissions.all().delete()

    def set_group(self, group_name):
        """Sets to the group and creates if the group does not exist."""
        if not Group.objects.filter(name=group_name):
            Group.objects.create(name=group_name)
        self._group = Group.objects.get(name=group_name)

    def get_group(self):
        return self._group

    def set_permission_profile(self, value_list):
        self._permission_profile = value_list
        if not value_list:
            self._permission_profile = ['add', 'change']

    def get_permission_profile(self):
        return self._permission_profile

    def set_visit_definitions(self, codes):
        from ..models import VisitDefinition
        self._visit_definitions = VisitDefinition.objects.filter(code__in=codes)
        if not self._visit_definitions:
            raise AttributeError(
                'Attribute visit_definitions cannot be None. '
                'Could not find any matching codes in {0}'.format(codes))

    def get_visit_definitions(self):
        return self._visit_definitions

    def set_content_types_by_visit_definition(self, codes):
        """Sets to a complete and unique list of content types
        from each Entry in the visit definition."""
        self._content_types = []
        for visit_definition in self.get_visit_definitions():
            for crf_entry in CrfEntry.objects.filter(visit_definition=visit_definition):
                if crf_entry.content_type_map.content_type not in self._content_types:
                    self._content_types.append(crf_entry.content_type_map.content_type)

    def set_content_types(self, app_label, models=None):
        """Set the list of content_types using the app_label and a
        list of models for that app_label.

        If models is None, will add all models for the app."""
        self._content_types = []
        if not models:
            for content_type in ContentType.objects.filter(app_label=app_label):
                self._content_types.append(content_type)
        else:
            for model in models:
                if not get_model(app_label, model):
                    raise AttributeError('Invalid model name {0}.{1}'.format(app_label, model))
            models = [model.lower() for model in models]
            for content_type in ContentType.objects.filter(app_label=app_label, model__in=models):
                self._content_types.append(content_type)

    def get_content_types(self):
        return self._content_types

    def message(self, msg):
        if self.show_messages:
            print(unicode(msg))
