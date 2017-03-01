import re

from django.apps import apps as django_apps
from django.db.utils import IntegrityError
from django.db import transaction

from ..site_labs import site_labs


class AliquotError(Exception):
    pass


class Aliquot:
    """A wrapper for the Aliquot model instance.
    """

    def __init__(self, obj):
        self._registered_subject = None
        self._registered_subject = None
        self.object = obj
        # set attrs from model fields
        for field in self.object._meta.fields:
            setattr(self, field.name, getattr(self.object, field.name))
        self.children = self.model.objects.filter(
            parent_identifier=self.aliquot_identifier).order_by(
                'aliquot_identifier')
        self.children_count = self.children.count()

    @property
    def model(self):
        app_name = 'edc_lab'
        app_config = django_apps.get_app_config(app_name)
        return django_apps.get_model(*app_config.aliquot_model.split('.'))

    def __str__(self):
        return self.aliquot_identifier

    def create_aliquots(self, process=None, numeric_code=None, aliquot_count=None):
        created = []
        if process:
            numeric_code = process.aliquot_type.numeric_code
            alpha_code = process.aliquot_type.alpha_code
            aliquot_count = process.aliquot_count
            aliquot_type = process.aliquot_type.name
        else:
            alpha_code = None
            aliquot_type = numeric_code
        if not re.match('\d+', numeric_code, re.ASCII):
            raise AliquotError(
                'Invalid aliquot type format. Expected numeric code. '
                'Got {}.'.format(numeric_code))
        for i in range(1, aliquot_count + 1):
            self.count += 1
            with transaction.atomic():
                try:
                    obj = self.model.objects.create(
                        aliquot_identifier=self.get_identifier(
                            numeric_code, i),
                        parent_identifier=self.object.aliquot_identifier,
                        identifier_prefix=self.object.identifier_prefix,
                        subject_identifier=self.object.subject_identifier,
                        requisition_identifier=self.object.requisition_identifier,
                        aliquot_type=aliquot_type,
                        numeric_code=numeric_code,
                        alpha_code=alpha_code,
                        count=self.count)
                except IntegrityError:
                    pass
                else:
                    created.append(obj)
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
        created_aliquots = []
        if not processing_profile:
            lab_profile = site_labs.get(lab_profile_name)
            if lab_profile:
                panel = lab_profile.panels.get(panel_name)
                processing_profile = panel.processing_profile
        try:
            for process in processing_profile.processes.values():
                created_aliquots.extend(self.create_aliquots(process))
        except AttributeError as e:
            if 'processes' not in str(e):
                raise AttributeError(e)
        return created_aliquots

    def get_identifier(self, numeric_code, count):
        prefix = self.aliquot_identifier[0:10]
        child_segment = self.aliquot_identifier[-4:]
        return prefix + child_segment + numeric_code + '{0:02d}'.format(count)
