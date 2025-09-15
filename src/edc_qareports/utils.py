import sys
from pathlib import Path
from warnings import warn

from django.apps import apps as django_apps
from django.conf import settings
from django.db import OperationalError, connection

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


def get_qareports_codenames(app_name: str, *note_models: str) -> list[str]:
    warn(
        "This function has been deprecated. Use get_app_codenames.",
        DeprecationWarning,
        2,
    )
    return get_app_codenames(app_name)


def recreate_db_view(model_cls, drop: bool | None = None, verbose: bool | None = None):
    """Manually recreate the database view for models declared
    with `django_db_views.DBView`.

    Mostly useful when Django raises an OperationalError with a
    restored DB complaining of 'The user specified as a definer
    (user@host) does not exist' or some variation of OperationalError
    with 'SELECT command denied to user...'

    This does not replace generating a migration with `viewmigration`
    and running the migration.

    For example:
        from intecomm_reports.models import Vl

        Vl.recreate_db_view()

    Also, could do something like this (replace details as required):
        CREATE USER 'edc-effect-live'@'10.131.23.168' IDENTIFIED BY 'xxxxxx';
        GRANT SELECT ON effect_prod.* to 'edc-effect-live'@'10.131.23.168';

    You can run through all models using this mixin and recreate:
        from django.apps import apps as django_apps
        from edc_qareports.model_mixins import QaReportModelMixin

        for model_cls in django_apps.get_models():
            if issubclass(model_cls, (QaReportModelMixin,)):
                print(model_cls)
                try:
                    model_cls.recreate_db_view()
                except AttributeError as e:
                    print(e)
                except TypeError as e:
                    print(e)
    """
    drop = True if drop is None else drop
    try:
        sql = model_cls.view_definition.get(settings.DATABASES["default"]["ENGINE"])
    except AttributeError as e:
        raise AttributeError(
            f"Is this model linked to a view? Declare model with `DBView`. Got {e}"
        )
    else:
        sql = sql.replace(";", "")
        if verbose:
            print(f"create view {model_cls._meta.db_table} as {sql};")
        with connection.cursor() as c:
            if drop:
                try:
                    c.execute(f"drop view {model_cls._meta.db_table};")
                except OperationalError:
                    pass
            c.execute(f"create view {model_cls._meta.db_table} as {sql};")
        if verbose:
            sys.stdout.write(
                f"Done. Refreshed DB VIEW `{model_cls._meta.db_table}` for model {model_cls}."
            )


def recreate_dbview_for_all():
    from .model_mixins import QaReportModelMixin

    for model_cls in django_apps.get_models():
        if issubclass(model_cls, (QaReportModelMixin,)):
            print(model_cls)
            try:
                model_cls.recreate_db_view()
            except AttributeError as e:
                print(e)
            except TypeError as e:
                print(e)
