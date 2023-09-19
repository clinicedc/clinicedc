from django.conf import settings


def get_languages_from_settings() -> dict[str, str]:
    """Returns a dictionary of language codes mapped to language names,
    for all languages defined in settings.LANGUAGES.
    """
    try:
        lang_iterator = settings.LANGUAGES.items()
    except AttributeError:
        lang_iterator = settings.LANGUAGES
    return {k: v for k, v in lang_iterator}
