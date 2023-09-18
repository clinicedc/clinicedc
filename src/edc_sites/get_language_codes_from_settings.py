from .get_languages_from_settings import get_languages_from_settings


def get_language_codes_from_settings() -> list[str]:
    """Returns a list of language codes, for all languages defined in
    settings.LANGUAGES.
    """
    return list(get_languages_from_settings().keys())
