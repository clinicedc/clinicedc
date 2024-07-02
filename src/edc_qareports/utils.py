from pathlib import Path

from django.conf import settings


def read_unmanaged_model_sql(
    filename: str | None = None,
    app_name: str | None = None,
    fullpath: str | Path | None = None,
) -> str:
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

    return " ".join(parsed_sql)
