import re

from django.apps import apps as django_apps
from django.db.utils import IntegrityError
from django.db import transaction

from .site_labs import site_labs

app_config = django_apps.get_app_config('edc_lab')


class AliquotError(Exception):
    pass


class Aliquot:
    """A wrapper for the Aliquot model instance.
    """

    model = django_apps.get_model(*app_config.aliquot_model.split('.'))

    def __init__(self, obj):
        self.object = obj
        for field in self.object._meta.fields:
            setattr(self, field.name, getattr(self.object, field.name))
        self.is_primary = self.object.is_primary
        self.children = self.model.objects.filter(
            parent_identifier=self.object.aliquot_identifier).order_by(
                'aliquot_identifier')
        self.count = self.children.count()

    def __str__(self):
        return self.aliquot_identifier

    def create_aliquots(self, numeric_code, aliquot_count):
        created = False
        if not re.match('\d+', numeric_code, re.ASCII):
            raise AliquotError(
                'Invalid aliquot type format. Expected numeric code. '
                'Got {}.'.format(numeric_code))
        for i in range(1, aliquot_count + 1):
            self.count += 1
            with transaction.atomic():
                try:
                    self.model.objects.create(
                        aliquot_identifier=self.get_identifier(
                            numeric_code, i),
                        parent_identifier=self.object.aliquot_identifier,
                        identifier_prefix=self.object.identifier_prefix,
                        subject_identifier=self.object.subject_identifier,
                        aliquot_type=numeric_code,
                        count=self.count)
                except IntegrityError:
                    pass
                else:
                    created = True
        return created

    def create_aliquot(self, numeric_code):
        self.create_aliquots(self, numeric_code, 1)

    def create_aliquots_by_processing_profile(self, panel_name=None,
                                              lab_profile_name=None,
                                              processing_profile=None,
                                              **kwargs):
        """Creates aliquots according to the processing profile.

        Typically lab_profile_name is requisition._meta.label_lower.
        """
        created = []
        processing_profile = processing_profile
        if not processing_profile:
            lab_profile = site_labs.get(lab_profile_name)
            if lab_profile:
                processing_profile = lab_profile.panels.get(
                    panel_name).processing_profile
        try:
            for process in processing_profile.processes.values():
                created.append(
                    self.create_aliquots(
                        process.aliquot_type.numeric_code, process.aliquot_count))
        except AttributeError as e:
            if 'processes' not in str(e):
                raise AttributeError(e)
        return created

    def get_identifier(self, numeric_code, count):
        prefix = self.aliquot_identifier[0:10]
        child_segment = self.aliquot_identifier[-4:]
        return prefix + child_segment + numeric_code + '{0:02d}'.format(count)
