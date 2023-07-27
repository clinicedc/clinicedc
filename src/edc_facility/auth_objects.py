from edc_auth.get_app_codenames import get_app_codenames

EDC_FACILITY = "EDC_FACILITY"
EDC_FACILITY_VIEW = "EDC_FACILITY_VIEW"
EDC_FACILITY_SUPER = "EDC_FACILITY_SUPER"

codenames = get_app_codenames("edc_facility")
codenames = [
    codename
    for codename in codenames
    if codename
    not in [
        "edc_facility.add_healthfacilitytypes",
        "edc_facility.change_healthfacilitytypes",
        "edc_facility.delete_healthfacilitytypes",
        "edc_facility.add_holiday",
        "edc_facility.change_holiday",
        "edc_facility.delete_holiday",
    ]
]
