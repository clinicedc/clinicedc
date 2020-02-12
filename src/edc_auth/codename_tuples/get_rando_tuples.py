from pprint import pprint

from edc_randomization.site_randomizers import site_randomizers


def get_rando_tuples():
    rando_tuples = []
    for randomizer_cls in site_randomizers._registry.values():
        app_label, model = randomizer_cls.model.split(".")
        rando_tuples.append(
            (f"{app_label}.view_{model}",
             f"Can view {randomizer_cls.model_cls()._meta.verbose_name}"))
        if not randomizer_cls.is_blinded_trial:
            rando_tuples.append(
                (f"{app_label}.display_{model}",
                 f"Can display {randomizer_cls.model_cls()._meta.verbose_name} assignment"))
    return rando_tuples
