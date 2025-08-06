"""
EXTRA_LANG_INFO is a dictionary structure to provide meta information
about 'custom' languages not provided by Django (i.e. those not already
defined in: django.conf.locale.LANG_INFO).

Use 2 digit (639-1) code over 3 digit (639-2) code where available

`code` src: https://www.loc.gov/standards/iso639-2/php/code_list.php
`name_local` src: https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
"""

EXTRA_LANG_INFO = {
    "lg": {
        "bidi": False,
        "code": "lg",
        "name": "Ganda",
        "name_local": "Luganda",
    },
    "mas": {
        "bidi": False,
        "code": "mas",
        "name": "Maasai",
        "name_local": "ɔl Maa",
    },
    "ry": {
        "bidi": False,
        "code": "ry",
        "name": "Runyakitara",
        "name_local": "Runyakitara",
    },
    "rny": {
        "bidi": False,
        "code": "rny",
        "name": "Runyankore",
        "name_local": "Runyankore",
    },
    "st": {
        "bidi": False,
        "code": "st",
        "name": "Sotho, Southern",
        "name_local": "Sesotho [southern]",
    },
    "tn": {
        "bidi": False,
        "code": "tn",
        "name": "Tswana",
        "name_local": "Setswana",
    },
    "xh": {
        "bidi": False,
        "code": "xh",
        "name": "Xhosa",
        "name_local": "isiXhosa",
    },
    "zu": {
        "bidi": False,
        "code": "zu",
        "name": "Zulu",
        "name_local": "isiZulu",
    },
}
