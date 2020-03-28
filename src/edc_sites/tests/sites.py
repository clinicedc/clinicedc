from edc_sites.single_site import SingleSite

fqdn = "clinicedc.org"

sites = [
    SingleSite(
        10,
        "mochudi",
        "Mochudi",
        country="botswana",
        country_code="bw",
        domain=f"mochudi.bw.{fqdn}",
    ),
    SingleSite(
        20,
        "molepolole",
        "molepolole",
        country="botswana",
        country_code="bw",
        fqdn=fqdn,
    ),
    SingleSite(
        30, "lobatse", "lobatse", country="botswana", country_code="bw", fqdn=fqdn,
    ),
    SingleSite(
        40, "gaborone", "gaborone", country="botswana", country_code="bw", fqdn=fqdn,
    ),
    SingleSite(
        50, "karakobis", "karakobis", country="botswana", country_code="bw", fqdn=fqdn,
    ),
    SingleSite(
        60, "windhoek", "windhoek", country="namibia", country_code="na", fqdn=fqdn,
    ),
]


more_sites = [
    SingleSite(
        60, "windhoek", "windhoek", country="namibia", country_code="na", fqdn=fqdn,
    ),
]

all_sites = {"botswana": sites, "namibia": more_sites}
all_test_sites = {"botswana": sites, "namibia": more_sites}
