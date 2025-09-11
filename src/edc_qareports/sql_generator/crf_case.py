from dataclasses import dataclass, field

import sqlglot
from django.apps import apps as django_apps
from django.db import OperationalError, connection

from .crf_subquery import CrfSubquery


class CrfCaseError(Exception):
    pass


@dataclass(kw_only=True)
class CrfCase:
    label: str = None
    dbtable: str = None
    label_lower: str = None
    fld_name: str | None = None
    where: str | None = None
    list_tables: list[tuple[str, str, str]] | None = field(default_factory=list)
    subjectvisit_dbtable: str | None = None

    @property
    def sql(self):
        sql = CrfSubquery(**self.__dict__).sql
        vendor = "postgres" if connection.vendor.startswith("postgres") else connection.vendor
        return sqlglot.transpile(sql, read="mysql", write=vendor)[0]

    @property
    def model_cls(self):
        return django_apps.get_model(self.label_lower)

    def fetchall(self):
        with connection.cursor() as cursor:
            try:
                cursor.execute(self.sql)
            except OperationalError as e:
                raise CrfCaseError(f"{e}. See {self}.")
            return cursor.fetchall()
