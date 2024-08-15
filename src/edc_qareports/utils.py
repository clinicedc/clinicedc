from pathlib import Path
from warnings import warn

from django.conf import settings
from edc_auth.get_app_codenames import get_app_codenames


def read_unmanaged_model_sql(
    filename: str | None = None,
    app_name: str | None = None,
    fullpath: str | Path | None = None,
) -> str:
    """Wait, use DBView instead!!"""
    uuid_func = "uuid()"
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
        uuid_func = "gen_random_uuid()"

    if not fullpath:
        fullpath = Path(settings.BASE_DIR) / app_name / "models" / "unmanaged" / filename
    else:
        fullpath = Path(fullpath)

    parsed_sql = []
    with fullpath.open("r") as f:
        for line in f:
            line = line.split("#", maxsplit=1)[0]
            line = line.split("-- ", maxsplit=1)[0]
            line = line.replace("\n", "")
            line = line.strip()
            if line:
                parsed_sql.append(line)

    sql = " ".join(parsed_sql)
    return sql.replace("uuid()", uuid_func)


def truncate_string(string: str, max_length: int) -> str:
    """Strips string of leading/trailing whitespace and truncates
    if > `max_length`.
    """
    string = string.strip()
    if len(string) > max_length:
        return string[: max_length - 1].strip() + "…"
    return string


def get_qareports_codenames(app_name: str, *note_models: str) -> list[str]:
    warn("This function has been deprecated. Use get_app_codenames.", DeprecationWarning, 2)
    return get_app_codenames(app_name)
