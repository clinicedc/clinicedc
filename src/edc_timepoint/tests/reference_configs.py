from edc_reference import ReferenceModelConfig, site_reference_configs


def register_to_site_reference_configs():
    site_reference_configs.registry = {}

    reference = ReferenceModelConfig(name="edc_metadata.CrfOne", fields=["f1", "f2", "f3"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_metadata.CrfTwo", fields=["f1"])
    site_reference_configs.register(reference)
