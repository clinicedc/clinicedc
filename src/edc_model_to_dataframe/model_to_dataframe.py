from __future__ import annotations

import contextlib
from copy import copy
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from clinicedc_constants import NULL_STRING
from django.apps import apps as django_apps
from django.core.exceptions import FieldError
from django.db.models import QuerySet
from django_crypto_fields.utils import get_encrypted_fields, has_encrypted_fields
from django_pandas.io import read_frame
from edc_sites.utils import get_site_model_cls

from .constants import ACTION_ITEM_COLUMNS, SYSTEM_COLUMNS

__all__ = ["ModelToDataframe", "ModelToDataframeError"]


if TYPE_CHECKING:
    pass


class ModelToDataframeError(Exception):
    pass


class ModelToDataframeRowCountError(Exception):
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

    This class extendd django_pandas read_frame since a model class
    may have M2M fields and read_frame does not handle M2M fields
    well. read_frame does not know about edc encrypted fields.

    m = ModelToDataframe(model='edc_pdutils.crf')
    my_df = m.dataframe

    See also: get_crf()
    """

    sys_field_names: tuple[str, ...] = (
        "_state",
        "_user_container_instance",
        "_domain_cache",
        "using",
        "slug",
    )
    edc_sys_columns: tuple[str, ...] = SYSTEM_COLUMNS
    action_item_columns: tuple[str, ...] = ACTION_ITEM_COLUMNS
    illegal_chars: dict[str, str] = {  # noqa: RUF012
        "\u2019": "'",
        "\u2018": "'",
        "\u201d": '"',
        "\u2013": "-",
        "\u2022": "*",
    }

    def __init__(
        self,
        model: str | None = None,
        queryset: [QuerySet] | None = None,
        query_filter: dict | None = None,
        decrypt: bool | None = None,
        drop_sys_columns: bool | None = None,
        drop_action_item_columns: bool | None = None,
        read_frame_verbose: bool | None = None,
        remove_timezone: bool | None = None,
        sites: list[int] | None = None,
    ):
        self._columns = None
        self._has_encrypted_fields = None
        self._list_model_related_columns = None
        self._encrypted_columns = None
        self._site_columns = None
        self._dataframe = pd.DataFrame()
        self._model_field_names: list[str] = []
        self.read_frame_verbose = False if read_frame_verbose is None else read_frame_verbose
        self.sites = sites
        self.drop_sys_columns = drop_sys_columns
        self.drop_action_item_columns = (
            True if drop_action_item_columns is None else drop_action_item_columns
        )
        self.decrypt = decrypt
        self.m2m_columns = []
        self.query_filter = query_filter or {}
        self.remove_timezone = True if remove_timezone is None else remove_timezone
        self.queryset = queryset
        self.model = queryset.model._meta.label_lower if self.queryset else model

        try:
            self.model_cls = django_apps.get_model(self.model)
        except LookupError as e:
            raise LookupError(f"Model is {self.model}. Got `{e}`") from e

        # by default exports for all sites
        if self.sites and (
            "site" in self.model_field_names or "site_id" in self.model_field_names
        ):
            self.query_filter.update({"site__in": self.sites})

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
        if self._dataframe.empty:
            model_row_count = (
                (self.queryset or self.model_cls.objects)
                .filter(**self.query_filter)
                .all()
                .count()
            )

            df = read_frame(
                (self.queryset or self.model_cls.objects)
                .values(*self.columns)
                .filter(**self.query_filter)
                .all(),
                verbose=self.read_frame_verbose,
            )[[col for col in self.columns]]

            self.validate_row_count(model_row_count, df, step_name="read_frame")

            df = self.merge_m2ms(df)

            self.validate_row_count(model_row_count, df, step_name="m2m")

            df = df.rename(columns=self.columns)

            # remove timezone if asked
            if self.remove_timezone:
                for column in list(
                    df.select_dtypes(include=["datetimetz", "datetime64"]).columns
                ):
                    df[column] = pd.to_datetime(df[column]).dt.tz_localize(None)

            # convert bool to int64
            for column in list(df.select_dtypes(include=["bool"]).columns):
                df[column] = df[column].astype("int64").replace({True: 1, False: 0})

            # convert object to str
            for column in list(df.select_dtypes(include=["object"]).columns):
                df[column] = df[column].fillna("")
                df[column] = df[column].astype(str)

            # convert timedeltas to secs
            for column in list(df.select_dtypes(include=["timedelta64"]).columns):
                df[column] = df[column].dt.total_seconds()

            # fillna
            df = df.fillna(value=np.nan, axis=0)

            # remove illegal chars
            for column in list(df.select_dtypes(include=["object"]).columns):
                df[column] = df.apply(lambda x, col=column: self._clean_chars(x[col]), axis=1)

            # check merges worked correctly
            self.validate_row_count(model_row_count, df, step_name="final")
            self._dataframe = df
        return self._dataframe

    def validate_row_count(
        self, model_row_count: int, df: pd.DataFrame, step_name: str
    ) -> bool:
        if model_row_count != len(df):
            model = (self.queryset or self.model_cls)._meta.label_lower
            raise ModelToDataframeRowCountError(
                "Dataframe row count mismatch. "
                f"See {model}. Expected {model_row_count}. Got {len(df)} at step {step_name}."
            )
        return True

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
                self.model_cls.objects.prefetch_related(m2m_field_name)
                .filter(**{f"{m2m_field_name}__isnull": False})
                .values("id", m2m_field_name)
            )
            df_m2m = (
                df_m2m.groupby("id")[m2m_field_name]
                .apply(",".join)
                .reset_index()
                .rename(columns={m2m_field_name: m2m_field_name.split("__")[0]})
            )
            dataframe = dataframe.merge(df_m2m, on="id", how="left").reset_index(drop=True)
        return dataframe

    def _clean_chars(self, s: str) -> str:
        if s:
            for k, v in self.illegal_chars.items():
                try:
                    s = s.replace(k, v)
                except (AttributeError, TypeError):
                    break
            return s
        return NULL_STRING

    def move_sys_columns_to_end(self, columns: dict[str, str]) -> dict[str, str]:
        system_columns = [
            f.name for f in self.model_cls._meta.get_fields() if f.name in SYSTEM_COLUMNS
        ]
        new_columns = {k: v for k, v in columns.items() if k not in system_columns}
        if (
            system_columns
            and len(new_columns.keys()) != len(columns.keys())
            and not self.drop_sys_columns
        ):
            new_columns.update({k: k for k in system_columns})
        return new_columns

    def move_action_item_columns(self, columns: dict[str, str]) -> dict[str, str]:
        action_item_columns = [
            f.name for f in self.model_cls._meta.get_fields() if f.name in ACTION_ITEM_COLUMNS
        ]
        new_columns = {k: v for k, v in columns.items() if k not in ACTION_ITEM_COLUMNS}
        if action_item_columns and (
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
        """Return a dictionary of column names for the Dataframe."""
        if not self._columns:
            columns = {col: col for col in self.model_field_names}
            for field_name in self.model_field_names:
                if field_name.endswith("_visit_id"):
                    with contextlib.suppress(FieldError):
                        columns = self.add_columns_for_subject_visit(field_name, columns)
                if field_name.endswith("_requisition") or field_name.endswith(
                    "requisition_id"
                ):
                    columns = self.add_columns_for_subject_requisitions(columns)
            columns = self.add_columns_for_site(columns)
            columns = self.add_list_model_name_columns(columns)
            columns = self.add_other_columns(columns)
            columns = self.add_subject_identifier_column(columns)
            columns = self.move_action_item_columns(columns)
            columns = self.move_sys_columns_to_end(columns)
            # ensure no encrypted fields were added
            if not self.decrypt:
                columns = {k: v for k, v in columns.items() if k not in self.encrypted_columns}
            self._columns = columns
        return self._columns

    @property
    def model_field_names(self) -> list[str]:
        if not self._model_field_names:
            self._model_field_names = [
                f.attname
                for f in self.model_cls._meta.get_fields()
                if f.concrete and not f.many_to_many
            ]
            for name in self.sys_field_names:
                with contextlib.suppress(ValueError):
                    self._model_field_names.remove(name)
            if not self.decrypt:
                self._model_field_names = [
                    col for col in self._model_field_names if col not in self.encrypted_columns
                ]
        return self._model_field_names

    @property
    def encrypted_columns(self) -> list[str]:
        """Return a sorted list of column names that use encryption."""
        if not self._encrypted_columns:
            self._encrypted_columns = list(
                set([f.name for f in get_encrypted_fields(self.model_cls)])
            )
            self._encrypted_columns.sort()
        return self._encrypted_columns

    @property
    def list_model_related_columns(self) -> list[str]:
        """Return a list of column names with fk to a ListModel."""
        from edc_list_data.model_mixins import (  # noqa: PLC0415
            ListModelMixin,
            ListUuidModelMixin,
        )

        if not self._list_model_related_columns:
            list_model_related_columns = []
            for fld_cls in self.model_cls._meta.get_fields():
                if (
                    hasattr(fld_cls, "related_model")
                    and fld_cls.related_model
                    and issubclass(fld_cls.related_model, (ListModelMixin, ListUuidModelMixin))
                ):
                    list_model_related_columns.append(fld_cls.attname)  # noqa: PERF401
            self._list_model_related_columns = list(set(list_model_related_columns))
        return self._list_model_related_columns

    @property
    def site_columns(self) -> list[str]:
        """Return a list of column names with fk to a site model."""

        if not self._site_columns:
            site_columns = []
            for fld_cls in self.model_cls._meta.get_fields():
                if (
                    hasattr(fld_cls, "related_model")
                    and fld_cls.related_model
                    and issubclass(fld_cls.related_model, (get_site_model_cls(),))
                ):
                    site_columns.append(fld_cls.attname)  # noqa: PERF401
            self._site_columns = list(set(site_columns))
        return self._site_columns

    @property
    def other_columns(self) -> list[str]:
        """Return OTHER column names with fk to a common models."""
        related_model = [get_site_model_cls(), django_apps.get_model("edc_lab.panel")]
        if not self._list_model_related_columns:
            list_model_related_columns = []
            for fld_cls in self.model_cls._meta.get_fields():
                if (
                    hasattr(fld_cls, "related_model")
                    and fld_cls.related_model
                    and fld_cls.related_model in related_model
                ):
                    list_model_related_columns.append(fld_cls.attname)  # noqa: PERF401
            self._list_model_related_columns = list(set(list_model_related_columns))
        return self._list_model_related_columns

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
        column_name: str, columns: dict[str, str]
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
    def add_columns_for_subject_requisitions(columns: dict[str, str]) -> dict[str, str]:
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

    def add_columns_for_site(self, columns: dict[str, str]) -> dict[str, str]:
        for col in copy(columns):
            if col in self.site_columns:
                col_prefix = col.split("_id")[0]
                columns.update({f"{col_prefix}__name": f"{col_prefix}_name"})
        return columns

    def add_list_model_name_columns(self, columns: dict[str, str]) -> dict[str, str]:
        for col in copy(columns):
            if col in self.list_model_related_columns:
                column_name = col.split("_id")[0]
                columns.update({f"{column_name}__name": f"{column_name}_name"})
        return columns

    def add_other_columns(self, columns: dict[str, str]) -> dict[str, str]:
        for col in copy(columns):
            if col in self.other_columns:
                column_name = col.split("_id")[0]
                columns.update({f"{column_name}__name": f"{column_name}_name"})
        return columns
