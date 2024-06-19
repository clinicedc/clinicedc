from pathlib import Path

from django.conf import settings


def read_unmanaged_model_sql(
    filename: str | None = None,
    app_name: str | None = None,
    fullpath: str | Path | None = None,
) -> str:
    if not fullpath:
        fullpath = Path(settings.BASE_DIR) / app_name / "models" / "unmanaged" / filename
    with fullpath.open("r") as f:
        sql = f.read()
    return sql.replace("\n", " ")
