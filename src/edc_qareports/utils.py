from pathlib import Path

from django.conf import settings


def read_unmanaged_model_sql(
    filename,
    app_name: str | None = None,
    fullpath: str | Path | None = None,
) -> str:
    file = Path(settings.BASE_DIR) / app_name / "models" / "unmanaged" / filename
    with file.open("r") as f:
        sql = f.read()
    return sql.replace("\n", " ")
