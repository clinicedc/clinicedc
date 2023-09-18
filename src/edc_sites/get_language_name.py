from .get_languages_from_settings import get_languages_from_settings


class InvalidLanguageCodeError(Exception):
    pass


def get_language_name(code) -> str:
    """Returns language name, given a language code defined in settings.LANGUAGES."""
    try:
        return get_languages_from_settings()[code]
    except KeyError:
        raise InvalidLanguageCodeError(
            "Unknown language code. Language code must be defined in settings.LANGUAGES. "
            f"Expected one of {get_languages_from_settings().keys()}.  Got '{code}'."
        )
