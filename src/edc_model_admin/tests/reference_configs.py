from edc_reference import ReferenceModelConfig, site_reference_configs


def register_to_site_reference_configs():
    site_reference_configs.registry = {}

    reference = ReferenceModelConfig(name="edc_model_admin.CrfOne", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_model_admin.CrfTwo", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_model_admin.CrfThree", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_model_admin.CrfFour", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_model_admin.CrfFive", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_model_admin.CrfSix", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(name="edc_model_admin.CrfSeven", fields=["f1"])
    site_reference_configs.register(reference)

    reference = ReferenceModelConfig(
        name="edc_model_admin.CrfMissingManager", fields=["f1"]
    )
    site_reference_configs.register(reference)
