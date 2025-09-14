from __future__ import annotations

import os
from textwrap import fill
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, TableStyle
from reportlab.platypus.flowables import KeepTogether, Spacer
from reportlab.platypus.tables import Table

from edc_data_manager.get_longitudinal_value import (
    DataDictionaryError,
    get_longitudinal_value,
)
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_randomization.auth_objects import RANDO_UNBLINDED
from edc_utils import formatted_age, get_static_file
from edc_utils.date import to_local

from .report import Report

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.core.handlers.wsgi import WSGIRequest

    from edc_crf.model_mixins import CrfModelMixin
    from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin


class NotAllowed(Exception):
    pass


class CrfPdfReportError(Exception):
    pass


class CrfPdfReport(Report):
    model: str = None  # label_lower
    report_url: str = None
    changelist_url: str = None

    default_page = dict(
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.5 * cm,
        pagesize=A4,
    )

    confidential = True
    draw_logo = True

    weight_model = None
    weight_field = "weight"

    open_label = True

    logo_data = {
        "app_label": "edc_pdf_reports",
        "filename": "clinicedc_logo.jpg",
        "first_page": (0.83 * cm, 0.83 * cm),
        "later_pages": (0.625 * cm, 0.625 * cm),
    }

    rando_user_group = None

    def __init__(
        self,
        model_obj: CrfModelMixin | UniqueSubjectIdentifierModelMixin = None,
        request: WSGIRequest | None = None,
        user: User | None = None,
        **extra_context,
    ):
        page: dict | None = extra_context.get("page")
        header_line: str | None = extra_context.get("header_line")
        filename: str | None = extra_context.get("filename")

        super().__init__(
            page=page, header_line=header_line, filename=filename, request=request
        )
        self._assignment = None
        self._logo = None
        self.model_obj = model_obj
        if not isinstance(self.model_obj, (self.get_model_cls(),)):
            raise CrfPdfReportError(
                f"Invalid model instance. Expected an instance of {self.get_model_cls()}. "
                f"Got {self.model_obj}."
            )
        if not self.changelist_url:
            raise CrfPdfReportError(f"Invalid changelist url. Got {self.changelist_url}.")

        self.user_model_cls = get_user_model()
        self.user = self.request.user if self.request else user
        self.subject_identifier = self.get_subject_identifier(**extra_context)
        self.bg_cmd = ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey)

    def __repr__(self):
        return f"{self.__class__.__name__}(model_obj={self.model_obj})"

    def __str__(self):
        return self.model_obj

    def get_subject_identifier(self, **kwargs) -> str:
        try:
            subject_identifier = self.model_obj.related_visit.subject_identifier
        except AttributeError:
            subject_identifier = self.model_obj.subject_identifier
        return subject_identifier

    @property
    def report_filename(self) -> str:
        timestamp = to_local(self.model_obj.report_datetime).strftime("%Y%m%d")
        report_filename = (
            f"{slugify(self.model_obj._meta.verbose_name.lower())}-{self.subject_identifier}-"
            f"{timestamp}.pdf"
        )
        return report_filename

    @classmethod
    def get_generic_report_filename(cls) -> str:
        return f"{slugify(cls.get_verbose_name().lower())}s.pdf"

    @classmethod
    def get_model_cls(cls) -> type[CrfModelMixin | UniqueSubjectIdentifierModelMixin]:
        return django_apps.get_model(cls.model)

    @classmethod
    def get_verbose_name(cls) -> str:
        return cls.get_model_cls()._meta.verbose_name

    def get_report_story(self, **kwargs):
        story = []
        return story

    def on_first_page(self, canvas, doc):
        super().on_first_page(canvas, doc)
        width, height = A4
        if self.draw_logo and self.logo:
            canvas.drawImage(
                self.logo, 35, height - 50, *self.logo_data["first_page"], mask="auto"
            )
        else:
            canvas.setFontSize(10)
            canvas.drawString(48, height - 40, ResearchProtocolConfig().protocol_name)
        if self.confidential:
            canvas.setFontSize(10)
            canvas.drawString(48, height - 50, "CONFIDENTIAL")
            canvas.drawRightString(width - 35, height - 50, "CONFIDENTIAL")

        canvas.setFontSize(10)
        canvas.drawRightString(width - 35, height - 40, self.title)

    def on_later_pages(self, canvas, doc):
        super().on_later_pages(canvas, doc)
        width, height = A4
        if self.draw_logo and self.logo:
            canvas.drawImage(
                self.logo, 35, height - 40, *self.logo_data["later_pages"], mask="auto"
            )
        if self.confidential:
            canvas.setFontSize(10)
            canvas.drawRightString(width - 35, height - 45, "CONFIDENTIAL")
        if self.title:
            canvas.setFontSize(8)
            canvas.drawRightString(width - 35, height - 35, self.title)

    def draw_demographics(self, story, **kwargs):
        try:
            assignment = fill(self.assignment, width=80)
        except NotAllowed:
            assignment = "*****************"
        rows = [
            ["Subject:", self.subject_identifier],
            [
                "Gender/Age:",
                f"{self.registered_subject.get_gender_display()} {self.age}",
            ],
            ["Weight:", f"{self.weight_at_timepoint} kg"],
            [
                "Study site:",
                f"{self.registered_subject.site.id}: "
                f"{self.registered_subject.site.name.title()}",
            ],
            [
                "Randomization date:",
                self.registered_subject.randomization_datetime.strftime("%Y-%m-%d %H:%M"),
            ],
            ["Assignment:", assignment],
        ]

        t = Table(rows, (4 * cm, 14 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        t.hAlign = "LEFT"
        story.append(t)

    @staticmethod
    def set_table_style(t, bg_cmd=None):
        cmds = [
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]
        if bg_cmd:
            cmds.append(bg_cmd)
        t.setStyle(TableStyle(cmds))
        t.hAlign = "LEFT"
        return t

    @staticmethod
    def history_change_message(obj):
        log_entry_model_cls = django_apps.get_model("admin.logentry")
        qs = log_entry_model_cls.objects.filter(
            action_time__gte=obj.modified, object_id=str(obj.id)
        ).order_by("action_time")
        log_entry = qs.first()
        try:
            soup = BeautifulSoup(log_entry.get_change_message(), features="html.parser")
            return soup.get_text()
        except AttributeError:
            return "--"

    def draw_narrative(self, story, title=None, text=None):
        t = Table([[title]], (18 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        p = Paragraph(text, self.styles["line_data_large"])
        p.hAlign = "LEFT"
        story.append(KeepTogether([t, Spacer(0.1 * cm, 0.5 * cm), p]))

    def draw_end_of_report(self, story):
        story.append(Paragraph("- End of report -", self.styles["line_label_center"]))

    @property
    def registered_subject(self):
        return django_apps.get_model("edc_registration.RegisteredSubject").objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def logo(self):
        if not self._logo:
            path = get_static_file(self.logo_data["app_label"], self.logo_data["filename"])
            if os.path.isfile(path):
                self._logo = ImageReader(path)
        return self._logo

    @property
    def title(self):
        verbose_name = self.model_obj.verbose_name.upper()
        subject_identifier = self.model_obj.subject_identifier
        return f"{verbose_name} FOR {subject_identifier}"

    @property
    def weight_at_timepoint(self):
        """Returns weight in Kgs"""
        try:
            return get_longitudinal_value(
                subject_identifier=self.subject_identifier,
                reference_dt=self.model_obj.report_datetime,
                **self.get_weight_model_and_field(),
            )
        except DataDictionaryError:
            return ""

    def get_weight_model_and_field(self):
        return {"model": self.weight_model, "field": self.weight_field}

    @property
    def age(self):
        model_obj = self.model_obj
        return formatted_age(
            self.registered_subject.dob, reference_dt=model_obj.report_datetime
        )

    @property
    def unblinded(self):
        """Override to determine if assignment can be shown
        for this subject_identifier.

        Default: True
        """
        return True

    @property
    def assignment(self):
        """Returns the assignment from the Randomization List"""
        if not self._assignment:
            if (
                not self.unblinded
                or not self.user.groups.filter(name=RANDO_UNBLINDED).exists()
            ):
                raise NotAllowed(
                    "User does not have permissions to access randomization list. "
                    f"Got {self.user}"
                )
            randomization_list_model_cls = django_apps.get_model(
                self.registered_subject.randomization_list_model
            )
            self._assignment = randomization_list_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            ).assignment_description
        return self._assignment

    def get_user(self, obj, field=None):
        field = field or "user_created"
        try:
            user = self.user_model_cls.objects.get(username=getattr(obj, field))
        except ObjectDoesNotExist:
            user_created = getattr(obj, field)
        else:
            user_created = f"{user.first_name} {user.last_name}"
        return user_created
