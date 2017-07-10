# intentionally blank
# needed for site_metadat_rules.autodiscover test
from edc_reference.reference_model_config import ReferenceModelConfig
from edc_reference.site import site_reference_fields


def register_to_site_reference_fields():
    site_reference_fields.registry = {}
    reference = ReferenceModelConfig(
        model='edc_metadata.SubjectRequisition',
        fields=['panel_name'])
    site_reference_fields.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfOne',
        fields=['f1', 'f2', 'f3'])
    site_reference_fields.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfTwo',
        fields=['f1'])
    site_reference_fields.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfThree',
        fields=['f1'])
    site_reference_fields.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfFour',
        fields=['f1'])
    site_reference_fields.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfFive',
        fields=['f1'])
    site_reference_fields.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfMissingManager',
        fields=['f1'])
    site_reference_fields.register(reference)
