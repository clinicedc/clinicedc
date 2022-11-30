from edc_sites.single_site import SingleSite

fqdn = "clinicedc.org"
languages = {"en": "English"}
sites: list[SingleSite] = [
    SingleSite(
        10,
        "mochudi",
        title="Mochudi",
        country="botswana",
        country_code="bw",
        languages=languages,
        domain=f"mochudi.bw.{fqdn}",
    ),
    SingleSite(
        20,
        "molepolole",
        title="Molepolole",
        country="botswana",
        country_code="bw",
        languages=languages,
        fqdn=fqdn,
    ),
    SingleSite(
        30,
        "lobatse",
        title="Lobatse",
        country="botswana",
        country_code="bw",
        languages=languages,
        fqdn=fqdn,
    ),
    SingleSite(
        40,
        "gaborone",
        title="Gaborone",
        country="botswana",
        country_code="bw",
        languages=languages,
        fqdn=fqdn,
    ),
    SingleSite(
        50,
        "karakobis",
        title="Karakobis",
        country="botswana",
        country_code="bw",
        languages=languages,
        fqdn=fqdn,
    ),
    SingleSite(
        60,
        "windhoek",
        title="Windhoek",
        country="namibia",
        country_code="na",
        languages=languages,
        fqdn=fqdn,
    ),
]


more_sites = [
    SingleSite(
        60,
        "windhoek",
        title="Windhoek",
        country="namibia",
        country_code="na",
        languages=languages,
        fqdn=fqdn,
    ),
]

all_sites = {"botswana": sites, "namibia": more_sites}
all_test_sites = {"botswana": sites, "namibia": more_sites}
