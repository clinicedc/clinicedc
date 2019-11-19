from edc_randomization.blinding import is_blinded_trial
from edc_randomization.utils import get_randomizationlist_model_name


def get_rando_tuples():
    app_label, model = get_randomizationlist_model_name().split(".")

    if is_blinded_trial():
        rando_tuples = [(f"{app_label}.view_{model}", "Can view randomization list")]
    else:
        rando_tuples = [
            (
                f"{app_label}.display_assignment",
                "Can display randomization assignment",
            ),
            (f"{app_label}.view_{model}", "Can view randomization list"),
        ]
    return rando_tuples
