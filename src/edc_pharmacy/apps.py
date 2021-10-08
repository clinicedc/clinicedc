from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_pharmacy"
    verbose_name = "Pharmacy"
    # prescription_model = "edc_pharmacy.prescription"
    # worklist_model = "edc_pharmacy.worklist"
    # template_name = None
    has_exportable_data = True
    include_in_administration_section = True
