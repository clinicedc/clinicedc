from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from django.apps import apps as django_apps
from django.core.exceptions import FieldError
from django.db import OperationalError
from django_crypto_fields.utils import has_encrypted_fields
from django_pandas.io import read_frame

from .constants import ACTION_ITEM_COLUMNS, SYSTEM_COLUMNS

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin

    class MyModel(SiteModelMixin, BaseUuidModel):
        class Meta(BaseUuidModel.Meta):
            pass


__all__ = ["ModelToDataframeError", "ModelToDataframe"]


class ModelToDataframeError(Exception):
    pass


class ModelToDataframe:
    """A class to return a model or queryset as a pandas dataframe
    with custom handling for EDC models.

    For a CRF, subject_identifier and a few other columns are added.
    Custom handles edc Site and Panel FK columns, list model FK, M2M,
    etc.  If model has an FK to subject_visit adds important columns
    from the SubjetVisit model (see `add_columns_for_subject_visit`).
    Protections are in place for models or related models with
    encrypted fields.

    We are not using django_pandas read_frame since a model class
    may have M2M fields and read_frame does not handle M2M fields
    well. read_frame does not know about edc encrypted fields.

    m = ModelToDataframe(model='edc_pdutils.crf')
    my_df = m.dataframe

    See also: get_crf()
    """

    sys_field_names: list[str] = [
        "_state",
        "_user_container_instance",
        "_domain_cache",
        "using",
        "slug",
    ]
    edc_sys_columns: list[str] = SYSTEM_COLUMNS
    action_item_columns: list[str] = ACTION_ITEM_COLUMNS
    illegal_chars: dict[str] = {
        "\u2019": "'",
        "\u2018": "'",
        "\u201d": '"',
        "\u2013": "-",
        "\u2022": "*",
    }

    def __init__(
        self,
        model: str | None = None,
        queryset: QuerySet | None = None,
        query_filter: dict | None = None,
        decrypt: bool | None = None,
        drop_sys_columns: bool | None = None,
        drop_action_item_columns: bool | None = None,
        read_frame_verbose: bool | None = None,
        verbose: bool | None = None,
        remove_timezone: bool | None = None,
        sites: list[int] | None = None,
    ):
        self._columns = None
        self._has_encrypted_fields = None
        self._list_columns = None
        self._encrypted_columns = None
        self._site_columns = None
        self._dataframe = pd.DataFrame()
        self.read_frame_verbose = False if read_frame_verbose is None else read_frame_verbose
        self.sites = sites
        self.drop_sys_columns = True if drop_sys_columns is None else drop_sys_columns
        self.drop_action_item_columns = (
            True if drop_action_item_columns is None else drop_action_item_columns
        )
        self.decrypt = decrypt
        self.m2m_columns = []
        self.query_filter = query_filter or {}
        self.verbose = verbose
        self.remove_timezone = True if remove_timezone is None else remove_timezone
        if queryset:
            self.model = queryset.model._meta.label_lower
        else:
            self.model = model
        try:
            self.model_cls = django_apps.get_model(self.model)
        except LookupError as e:
            raise LookupError(f"Model is {self.model}. Got `{e}`")
        if self.sites:
            try:
                if queryset:
                    self.queryset = queryset.filter(site__in=sites)
                else:
                    self.queryset = self.model_cls.objects.filter(site__in=sites)
            except FieldError as e:
                if "Cannot resolve keyword 'site' into field" not in str(e):
                    raise
                self.queryset = queryset or self.model_cls.objects.all()
        else:
            self.queryset = queryset or self.model_cls.objects.all()
        # trigger query
        self.row_count = self.get_row_count()

    def get_row_count(self):
        try:
            row_count = self.queryset.count()
        except OperationalError as e:
            if "The user specified as a definer" in str(e) and getattr(
                self.model_cls, "recreate_db_view"
            ):
                self.model_cls.recreate_db_view()
                row_count = self.queryset.count()
            else:
                raise
        return row_count

    @property
    def dataframe(self) -> pd.DataFrame:
        """Returns a pandas dataframe.

        Warning:
            If any column names collide, 'rename()' converts column
            datatype from Series to Dataframe and an error will be
            raised later on. For example, main model "visit_reason"
            and "subject_visit.visit_reason" -- in the '_dataframe',
            column "visit_reason" would become a Dataframe instead
            of a Series like all other columns.
        """
        if self._dataframe.empty and self.row_count > 0:
            if self.decrypt and self.has_encrypted_fields:
                dataframe = self.get_dataframe_with_encrypted_fields(self.row_count)
            else:
                dataframe = self.get_dataframe_without_encrypted_fields()

            dataframe = self.merge_m2ms(dataframe)

            dataframe.rename(columns=self.columns, inplace=True)

            # remove timezone if asked
            if self.remove_timezone:
                for column in list(dataframe.select_dtypes(include=["datetimetz"]).columns):
                    dataframe[column] = pd.to_datetime(dataframe[column]).dt.tz_localize(None)

            # convert bool to int64
            for column in list(dataframe.select_dtypes(include=["bool"]).columns):
                dataframe[column] = (
                    dataframe[column].astype("int64").replace({True: 1, False: 0})
                )

            # convert object to str
            for column in list(dataframe.select_dtypes(include=["object"]).columns):
                dataframe[column] = dataframe[column].fillna("")
                dataframe[column] = dataframe[column].astype(str)

            # convert timedeltas to secs
            for column in list(dataframe.select_dtypes(include=["timedelta64"]).columns):
                dataframe[column] = dataframe[column].dt.total_seconds()

            # fillna
            dataframe.fillna(value=np.nan, axis=0, inplace=True)

            # remove illegal chars
            for column in list(dataframe.select_dtypes(include=["object"]).columns):
                dataframe[column] = dataframe.apply(
                    lambda x: self._clean_chars(x[column]), axis=1
                )
            self._dataframe = dataframe
        return self._dataframe

    def get_dataframe_without_encrypted_fields(self) -> pd.DataFrame:
        queryset = self.queryset.values_list(*self.columns).filter(**self.query_filter)
        return pd.DataFrame(list(queryset), columns=[v for v in self.columns])

    def get_dataframe_with_encrypted_fields(self, row_count: int) -> pd.DataFrame:
        df = read_frame(
            self.queryset.filter(**self.query_filter), verbose=self.read_frame_verbose
        )
        return df[[col for col in self.columns]]

    def merge_m2ms(self, dataframe):
        """Merge m2m data into main dataframe.

        If m2m field name is not "name", add a class attr to
        the m2m model that returns a field_name.

        For example:

            # see edc_model_to_dataframe
            m2m_related_field = "patient_log_identifier"

        """
        for m2m_field in self.model_cls._meta.many_to_many:
            if getattr(m2m_field.related_model, "m2m_related_field", None):
                related_field = m2m_field.related_model.m2m_related_field
            else:
                related_field = "name"

            if related_field not in [
                f.name for f in m2m_field.related_model._meta.get_fields()
            ]:
                raise ModelToDataframeError(
                    f"m2m model missing `{related_field}` field. "
                    f"Parent model is {self.model_cls}. "
                    f"Got {m2m_field.related_model}. Try adding attribute "
                    "m2m_related_field={model_name: field_name} to model class "
                    f"{m2m_field.related_model}"
                )
            m2m_field_name = f"{m2m_field.name}__{related_field}"
            df_m2m = read_frame(
                self.model_cls.objects.filter(**{f"{m2m_field_name}__isnull": False}).values(
                    "id", m2m_field_name
                )
            )
            df_m2m = df_m2m.groupby("id")[m2m_field_name].apply(",".join).reset_index()
            df_m2m = df_m2m.rename(columns={m2m_field_name: m2m_field_name.split("__")[0]})
            dataframe = dataframe.merge(df_m2m, on="id", how="left")
        return dataframe

    def _clean_chars(self, s):
        try:
            s = s if s else s
        except ValueError:
            pass
        else:
            if s:
                for k, v in self.illegal_chars.items():
                    try:
                        s = s.replace(k, v)
                    except (AttributeError, TypeError):
                        break
        return s

    def move_sys_columns_to_end(self, columns: dict[str, str]) -> dict[str, str]:
        system_columns = [
            f.name for f in self.model_cls._meta.get_fields() if f.name in SYSTEM_COLUMNS
        ]
        new_columns = {k: v for k, v in columns.items() if k not in system_columns}
        if system_columns:
            if len(new_columns.keys()) != len(columns.keys()) and not self.drop_sys_columns:
                new_columns.update({k: k for k in system_columns})
        return new_columns

    def move_action_item_columns(self, columns: dict[str, str]) -> dict[str, str]:
        action_item_columns = [
            f.name for f in self.model_cls._meta.get_fields() if f.name in ACTION_ITEM_COLUMNS
        ]
        new_columns = {k: v for k, v in columns.items() if k not in ACTION_ITEM_COLUMNS}
        if action_item_columns:
            if (
                len(new_columns.keys()) != len(columns.keys())
                and not self.drop_action_item_columns
            ):
                new_columns.update({k: k for k in ACTION_ITEM_COLUMNS})
        return new_columns

    @property
    def has_encrypted_fields(self) -> bool:
        """Returns True if at least one field uses encryption."""
        if self._has_encrypted_fields is None:
            self._has_encrypted_fields = has_encrypted_fields(self.model_cls)
        return self._has_encrypted_fields

    @property
    def columns(self) -> dict[str, str]:
        """Return a dictionary of column names."""
        if not self._columns:
            columns_list = self.get_columns_list()
            columns = dict(zip(columns_list, columns_list))
            for column_name in columns_list:
                if column_name.endswith("_visit_id"):
                    try:
                        columns = self.add_columns_for_subject_visit(
                            column_name=column_name, columns=columns
                        )
                    except FieldError:
                        pass
                if column_name.endswith("_requisition") or column_name.endswith(
                    "requisition_id"
                ):
                    columns = self.add_columns_for_subject_requisitions(columns)
            columns = self.add_columns_for_site(columns=columns)
            columns = self.add_list_model_name_columns(columns)
            columns = self.add_other_columns(columns)
            columns = self.add_subject_identifier_column(columns)
            columns = self.move_action_item_columns(columns)
            columns = self.move_sys_columns_to_end(columns)
            self._columns = columns
        return self._columns

    def get_columns_list(self) -> list[str]:
        try:
            columns_list = list(self.queryset[0].__dict__.keys())
        except AttributeError as e:
            if "__dict__" in str(e):
                columns_list = list(self.queryset._fields)
            else:
                raise
        for name in self.sys_field_names:
            try:
                columns_list.remove(name)
            except ValueError:
                pass
        if not self.decrypt and self.has_encrypted_fields:
            columns_list = [col for col in columns_list if col not in self.encrypted_columns]
        return columns_list

    @property
    def encrypted_columns(self) -> list[str]:
        """Return a list of column names that use encryption."""
        if not self._encrypted_columns:
            self._encrypted_columns = ["identity"]
            for field in self.model_cls._meta.get_fields():
                if hasattr(field, "field_cryptor"):
                    self._encrypted_columns.append(field.name)
            self._encrypted_columns = list(set(self._encrypted_columns))
            self._encrypted_columns.sort()
        return self._encrypted_columns

    @property
    def list_columns(self) -> list[str]:
        """Return a list of column names with fk to a list model."""
        from edc_list_data.model_mixins import ListModelMixin, ListUuidModelMixin

        if not self._list_columns:
            list_columns = []
            for fld_cls in self.model_cls._meta.get_fields():
                if (
                    hasattr(fld_cls, "related_model")
                    and fld_cls.related_model
                    and issubclass(fld_cls.related_model, (ListModelMixin, ListUuidModelMixin))
                ):
                    list_columns.append(fld_cls.attname)
            self._list_columns = list(set(list_columns))
        return self._list_columns

    @property
    def site_columns(self) -> list[str]:
        """Return a list of column names with fk to a site model."""
        from django.contrib.sites.models import Site

        if not self._site_columns:
            site_columns = []
            for fld_cls in self.model_cls._meta.get_fields():
                if (
                    hasattr(fld_cls, "related_model")
                    and fld_cls.related_model
                    and issubclass(fld_cls.related_model, (Site,))
                ):
                    site_columns.append(fld_cls.attname)
            self._site_columns = list(set(site_columns))
        return self._site_columns

    @property
    def other_columns(self) -> list[str]:
        """Return other column names with fk to a common models."""
        from django.contrib.sites.models import Site
        from edc_lab.models import Panel

        related_model = [Site, Panel]
        if not self._list_columns:
            list_columns = []
            for fld_cls in self.model_cls._meta.get_fields():
                if (
                    hasattr(fld_cls, "related_model")
                    and fld_cls.related_model
                    and fld_cls.related_model in related_model
                ):
                    list_columns.append(fld_cls.attname)
            self._list_columns = list(set(list_columns))
        return self._list_columns

    def add_subject_identifier_column(self, columns: dict[str, str]) -> dict[str, str]:
        if "subject_identifier" not in [v for v in columns.values()]:
            subject_identifier_column = None
            id_columns = [col.replace("_id", "") for col in columns if col.endswith("_id")]
            for col in id_columns:
                field = getattr(self.model_cls, col, None)
                if field and [
                    fld.name
                    for fld in field.field.related_model._meta.get_fields()
                    if fld.name == "subject_identifier"
                ]:
                    subject_identifier_column = f"{col}__subject_identifier"
                    break
            if subject_identifier_column:
                columns.update({subject_identifier_column: "subject_identifier"})
        return columns

    @staticmethod
    def add_columns_for_subject_visit(
        column_name: str = None, columns: dict[str, str] = None
    ) -> dict[str, str]:
        if "subject_identifier" not in [v for v in columns.values()]:
            columns.update(
                {f"{column_name}__appointment__subject_identifier": "subject_identifier"}
            )
        columns.update({f"{column_name}__appointment__appt_datetime": "appointment_datetime"})
        columns.update({f"{column_name}__appointment__visit_code": "visit_code"})
        columns.update(
            {f"{column_name}__appointment__visit_code_sequence": "visit_code_sequence"}
        )
        columns.update({f"{column_name}__report_datetime": "visit_datetime"})
        columns.update({f"{column_name}__reason": "visit_reason"})
        return columns

    @staticmethod
    def add_columns_for_subject_requisitions(columns: dict[str, str] = None) -> dict[str, str]:
        for col in copy(columns):
            if col.endswith("_requisition_id"):
                col_prefix = col.split("_")[0]
                column_name = col.split("_id")[0]
                columns.update(
                    {
                        f"{column_name}__requisition_identifier": (
                            f"{col_prefix}_requisition_identifier"
                        )
                    }
                )
                columns.update(
                    {f"{column_name}__drawn_datetime": f"{col_prefix}_drawn_datetime"}
                )
                columns.update({f"{column_name}__is_drawn": f"{col_prefix}_is_drawn"})
        return columns

    def add_columns_for_site(self, columns: dict[str, str] = None) -> dict[str, str]:
        for col in copy(columns):
            if col in self.site_columns:
                col_prefix = col.split("_id")[0]
                columns.update({f"{col_prefix}__name": f"{col_prefix}_name"})
        return columns

    def add_list_model_name_columns(self, columns: dict[str, str] = None) -> dict[str, str]:
        for col in copy(columns):
            if col in self.list_columns:
                column_name = col.split("_id")[0]
                columns.update({f"{column_name}__name": f"{column_name}_name"})
        return columns

    def add_other_columns(self, columns: dict[str, str] = None) -> dict[str, str]:
        for col in copy(columns):
            if col in self.other_columns:
                column_name = col.split("_id")[0]
                columns.update({f"{column_name}__name": f"{column_name}_name"})
        return columns
