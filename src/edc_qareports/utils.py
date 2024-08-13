from pathlib import Path

from django.conf import settings

"""
use DBView instead
"""


def read_unmanaged_model_sql(
    filename: str | None = None,
    app_name: str | None = None,
    fullpath: str | Path | None = None,
) -> str:
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
