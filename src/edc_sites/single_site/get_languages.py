from .get_languages_from_settings import get_languages_from_settings


class SiteLanguagesError(Exception):
    pass


def get_languages(language_codes: list[str], site_id: int) -> dict[str, str]:
    defined_languages = get_languages_from_settings()
    if language_codes:
        if unknown_language_codes := [c for c in language_codes if c not in defined_languages]:
            raise SiteLanguagesError(
                "Unknown language code(s) associated with site. Language code must be "
                "defined in settings.LANGUAGES. "
                f"Expected one of {list(defined_languages.keys())}. "
                f"Got {unknown_language_codes} for site `{site_id}`."
            )
        languages = {code: defined_languages[code] for code in language_codes}
    else:
        languages = defined_languages
    return languages
