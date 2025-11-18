import contextlib
import sys
from warnings import warn

from django.apps import apps as django_apps
from django.conf import settings
from django.db import OperationalError, connection
from edc_auth.get_app_codenames import get_app_codenames


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
        ) from e
    else:
        sql = sql.replace(";", "")
        if verbose:
            sys.stdout.write(f"create view {model_cls._meta.db_table} as {sql};\n")
        with connection.cursor() as c:
            if drop:
                with contextlib.suppress(OperationalError):
                    c.execute(f"drop view {model_cls._meta.db_table};")
            c.execute(f"create view {model_cls._meta.db_table} as {sql};")
        if verbose:
            sys.stdout.write(
                f"Done. Refreshed DB VIEW `{model_cls._meta.db_table}` for model {model_cls}."
            )


def recreate_dbview_for_all():
    from .model_mixins import QaReportModelMixin  # noqa: PLC0415

    for model_cls in django_apps.get_models():
        if issubclass(model_cls, (QaReportModelMixin,)):
            sys.stdout.write(f"{model_cls}\n")
            try:
                model_cls.recreate_db_view()
            except AttributeError as e:
                sys.stdout.write(f"{e}\n")
            except TypeError as e:
                sys.stdout.write(f"{e}\n")
