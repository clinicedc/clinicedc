from dataclasses import dataclass, field

from django.apps import apps as django_apps
from django.db import OperationalError, connection

from .subquery_from_dict import subquery_from_dict


class QaCaseError(Exception):
    pass


@dataclass(kw_only=True)
class QaCase:
    label: str = None
    dbtable: str = None
    label_lower: str = None
    fld_name: str | None = None
    where: str | None = None
    list_tables: list[tuple[str, str, str]] | None = field(default_factory=list)

    def __post_init__(self):
        if self.fld_name is None and self.where is None:
            raise QaCaseError("Expected either 'fld_name' or 'where'. Got None for both.")
        elif self.fld_name is not None and self.where is not None:
            raise QaCaseError("Expected either 'fld_name' or 'where', not both.")

    @property
    def sql(self):
        return subquery_from_dict([self.__dict__])

    @property
    def model_cls(self):
        return django_apps.get_model(self.label_lower)

    def fetchall(self):
        sql = subquery_from_dict([self.__dict__])
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
            except OperationalError as e:
                raise QaCaseError(f"{e}. See {self}.")
            return cursor.fetchall()
