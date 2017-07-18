# intentionally blank
# needed for site_metadat_rules.autodiscover test
from edc_reference import ReferenceModelConfig, site_reference_configs


def register_to_site_reference_configs():
    site_reference_configs.registry = {}
    reference = ReferenceModelConfig(
        model='edc_metadata.SubjectRequisition',
        fields=['panel_name'])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfOne',
        fields=['f1', 'f2', 'f3'])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfTwo',
        fields=['f1'])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfThree',
        fields=['f1'])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfFour',
        fields=['f1'])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfFive',
        fields=['f1'])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        model='edc_metadata.CrfMissingManager',
        fields=['f1'])
    site_reference_configs.register(reference)
