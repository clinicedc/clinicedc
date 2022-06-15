import os
from textwrap import fill

from bs4 import BeautifulSoup
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from edc_data_manager.get_longitudinal_value import (
    DataDictionaryError,
    get_longitudinal_value,
)
from edc_protocol import Protocol
from edc_randomization.auth_objects import RANDO_UNBLINDED
from edc_utils import formatted_age, get_static_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, TableStyle
from reportlab.platypus.flowables import KeepTogether, Spacer
from reportlab.platypus.tables import Table

from .report import Report


class NotAllowed(Exception):
    pass


class CrfPdfReportError(Exception):
    pass


class CrfPdfReport(Report):
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

    model_attr = "object"

    rando_user_group = None

    def __init__(self, subject_identifier=None, **kwargs):
        super().__init__(**kwargs)
        self._assignment = None
        self._logo = None
        self.user_model_cls = get_user_model()
        self.bg_cmd = ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey)
        self.subject_identifier = subject_identifier

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
    def model_obj(self):
        return getattr(self, self.model_attr)

    @property
    def registered_subject(self):
        return django_apps.get_model("edc_registration.RegisteredSubject").objects.get(
            subject_identifier=self.subject_identifier
        )

    @property
    def age(self):
        model_obj = getattr(self, self.model_attr)
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
                or not self.request.user.groups.filter(name=RANDO_UNBLINDED).exists()
            ):
                raise NotAllowed(
                    "User does not have permissions to access randomization list. "
                    f"Got {self.request.user}"
                )
            randomization_list_model_cls = django_apps.get_model(
                self.registered_subject.randomization_list_model
            )
            self._assignment = randomization_list_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            ).assignment_description
        return self._assignment

    @property
    def logo(self):
        if not self._logo:
            path = get_static_file(self.logo_data["app_label"], self.logo_data["filename"])
            if os.path.isfile(path):
                self._logo = ImageReader(path)
        return self._logo

    @property
    def title(self):
        verbose_name = getattr(self, self.model_attr).verbose_name.upper()
        subject_identifier = getattr(self, self.model_attr).subject_identifier
        return f"{verbose_name} FOR {subject_identifier}"

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

    def draw_end_of_report(self, story):
        story.append(Paragraph("- End of report -", self.styles["line_label_center"]))

    def get_user(self, obj, field=None):
        field = field or "user_created"
        try:
            user = self.user_model_cls.objects.get(username=getattr(obj, field))
        except ObjectDoesNotExist:
            user_created = getattr(obj, field)
        else:
            user_created = f"{user.first_name} {user.last_name}"
        return user_created

    def on_first_page(self, canvas, doc):
        super().on_first_page(canvas, doc)
        width, height = A4
        if self.draw_logo and self.logo:
            canvas.drawImage(
                self.logo, 35, height - 50, *self.logo_data["first_page"], mask="auto"
            )
        else:
            canvas.setFontSize(10)
            canvas.drawString(48, height - 40, Protocol().protocol_name)
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
