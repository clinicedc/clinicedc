from edc_randomization.blinding import is_blinded_trial

if is_blinded_trial():
    rando_tuples = [
        ("edc_randomization.view_randomizationlist", "Can view randomization list")
    ]
else:
    rando_tuples = [
        (
            "edc_randomization.display_assignment",
            "Can display randomization assignment",
        ),
        ("edc_randomization.view_randomizationlist", "Can view randomization list"),
    ]
