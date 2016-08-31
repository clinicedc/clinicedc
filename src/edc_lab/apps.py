import copy

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig

from .panel import Panel
from .aliquot.aliquot_type import AliquotType
from .aliquot.processing_profile import ProcessingProfile, Process


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    app_label = 'edc_example'

    aliquot_types = [
        AliquotType('Whole Blood', 'WB', '02', allowed_derivatives=['BC', 'PL']),
        AliquotType('Plasma', 'PL', '36', allowed_derivatives=None),
        AliquotType('Buffy Coat', 'BC', '12', allowed_derivatives=None),
    ]

    panels = [
        Panel('Viral Load', 'WB', processing_profile='viral_load'),
        Panel('Research Blood Draw', 'WB', processing_profile='pbmc')
    ]

    processing_profiles = [
        ProcessingProfile('viral_load', 'WB', processes=[Process('PL', 4), Process('BC', 3)]),
        ProcessingProfile('pbmc', 'WB', processes=[Process('PL', 4)]),
    ]

    def ready(self):
        from .signals import packing_list_on_post_save, requisition_identifier_on_post_save
        self.aliquot_types_to_dict()
        self.processing_profiles_to_dict()
        self.panels_to_dict()

    @property
    def aliquot_model(self):
        return django_apps.get_model(self.app_label, 'aliquot')

    def aliquot_types_to_dict(self):
        aliquot_types = copy.copy(self.aliquot_types)
        self.aliquot_types = {}
        for aliquot_type in aliquot_types:
            self.aliquot_types[aliquot_type.numeric_code] = aliquot_type
            self.aliquot_types[aliquot_type.alpha_code] = aliquot_type

    def processing_profiles_to_dict(self):
        processing_profiles = copy.copy(self.processing_profiles)
        self.processing_profiles = {}
        for processing_profile in processing_profiles:
            processing_profile.aliquot_type = self.aliquot_types[processing_profile.aliquot_type]
            for process in processing_profile.processes:
                process.aliquot_type = self.aliquot_types[process.aliquot_type]
                processing_profile.process = process
            self.processing_profiles[processing_profile.name] = processing_profile

    def panels_to_dict(self):
        panels = copy.copy(self.panels)
        self.panels = {}
        for panel in panels:
            panel.aliquot_type = self.aliquot_types[panel.aliquot_type]
            self.panels[panel.name] = panel
            self.panels[panel.name].processing_profile = self.processing_profiles[panel.processing_profile]
