from tempfile import mkdtemp

from django.contrib import messages
from edc_constants.constants import YES
from edc_identifier.utils import convert_to_human_readable
from edc_lab.model_mixins import RequisitionModelMixin
from edc_lab.models.manifest.shipper import Shipper
from edc_pdf_reports import Report
from edc_utils import get_utcnow
from reportlab.graphics.barcode import code39
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


class RequisitionReport(Report):
    def __init__(
        self,
        appointment=None,
        selected_panel_names=None,
        consignee=None,
        request=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._requisitions = []
        self.request = request
        self.selected_panel_names = selected_panel_names
        self.site = request.site
        self.appointment = appointment
        self.user = request.user
        self.consignee = consignee
        self.contact_name = f"{self.user.first_name} {self.user.last_name}"
        self.image_folder = mkdtemp()
        self.timestamp = get_utcnow().strftime("%Y%m%d%H%M%S")
        self.report_filename = f"requisition_{self.timestamp}.pdf"

    @property
    def shipper(self):
        """Return a shipper model instance."""
        try:
            shipper = Shipper.objects.all()[0]
        except IndexError:
            messages.error(self.request, "Unable to print report. Please define the shipper.")
            shipper = Shipper()
        return shipper

    def get_report_story(self, **kwargs):
        story = [
            Paragraph(
                "PATIENT SPECIMEN REQUISITION / MANIFEST",
                self.styles["line_label_center"],
            )
        ]

        data = [
            [
                Paragraph("DATE", self.styles["line_label"]),
                Paragraph("REFERENCE", self.styles["line_label"]),
            ],
            [
                Paragraph(get_utcnow().strftime("%Y-%m-%d"), self.styles["line_data_largest"]),
                Paragraph(
                    convert_to_human_readable(self.timestamp),
                    self.styles["line_data_largest"],
                ),
            ],
        ]
        t = Table(data)
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (1, 0), 0.25, colors.black),
                    ("INNERGRID", (0, 1), (1, 1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(t)

        data = [
            [
                Paragraph("FROM (complete name and address)", self.styles["line_label"]),
                Paragraph("DELIVER TO (complete name and address)", self.styles["line_label"]),
            ],
            [
                Paragraph(
                    self.formatted_address(**self.shipper_data),
                    self.styles["line_data_large"],
                ),
                Paragraph(
                    self.formatted_address(**self.consignee_data),
                    self.styles["line_data_large"],
                ),
            ],
        ]

        t = Table(data)
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (1, 0), 0.25, colors.black),
                    ("INNERGRID", (0, 1), (1, 1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(t)

        data = [
            [
                Paragraph("CLINIC NAME", self.styles["line_label"]),
                Paragraph("INSTRUCTIONS<br />", self.styles["line_label"]),
            ],
            [
                Paragraph(self.site.name.title(), self.styles["line_data_large"]),
                Paragraph(self.description or "", self.styles["line_data"]),
            ],
            [Paragraph("TEL/MOBILE/FAX", self.styles["line_label"]), ""],
            [
                Paragraph(
                    f'T:{self.shipper.telephone or "?"} M:{self.shipper.mobile or "?"} '
                    f'F:{self.shipper.fax or "?"}',
                    self.styles["line_data_large"],
                ),
                "",
            ],
            [Paragraph("EMAIL", self.styles["line_label"]), ""],
            [Paragraph(self.shipper.email or "", self.styles["line_data_large"]), ""],
        ]
        t1 = Table(data)
        t1.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 1), (0, 2), 0.25, colors.black),
                    ("INNERGRID", (0, 3), (0, 4), 0.25, colors.black),
                    ("INNERGRID", (0, 0), (1, 0), 0.25, colors.black),
                    ("INNERGRID", (0, 1), (1, 1), 0.25, colors.black),
                    ("INNERGRID", (0, 2), (1, 2), 0.25, colors.black),
                    ("INNERGRID", (0, 3), (1, 3), 0.25, colors.black),
                    ("INNERGRID", (0, 4), (1, 4), 0.25, colors.black),
                    ("INNERGRID", (0, 5), (1, 5), 0.25, colors.black),
                    ("SPAN", (1, 1), (1, 5)),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(t1)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(
            Table(
                [
                    [
                        Paragraph(
                            "I DECLARE THE INFORMATION TO BE TRUE AND CORRECT",
                            self.styles["line_label"],
                        )
                    ]
                ]
            )
        )

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        data = [
            [
                Paragraph(self.contact_name, self.styles["line_data_large"]),
                "",
                Paragraph(
                    get_utcnow().strftime("%Y-%m-%d %H:%M"),
                    self.styles["line_data_large"],
                ),
            ],
            [
                Paragraph("SIGNATURE (sign next to your name.)", self.styles["line_label"]),
                "",
                Paragraph("DATE", self.styles["line_label"]),
            ],
        ]

        t1 = Table(data, colWidths=(None, 2 * cm, None))
        t1.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (0, 1), 0.25, colors.black),
                    ("INNERGRID", (2, 0), (2, 1), 0.25, colors.black),
                ]
            )
        )

        story.append(t1)
        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(
            Paragraph(
                "Place a check-mark in the right-most column for each specimen received.",
                self.styles["line_label"],
            )
        )

        story = self.append_requisition_items_story(story)

        story.append(Spacer(0.1 * cm, 1 * cm))

        story.append(Paragraph("Comments (if any):", self.styles["line_label"]))
        story.append(Spacer(0.1 * cm, 2 * cm))

        story.append(
            Paragraph(
                "The above items marked with a check have been received in good order:",
                self.styles["line_label"],
            )
        )

        story.append(Spacer(0.1 * cm, 1 * cm))

        data = [
            [
                Paragraph("", self.styles["line_data_large"]),
                "",
                Paragraph("", self.styles["line_data_large"]),
            ],
            [
                Paragraph(
                    "SIGNATURE OF LABORATORY TECHNICIAN (Write name and sign.)",
                    self.styles["line_label"],
                ),
                "",
                Paragraph("DATE", self.styles["line_label"]),
            ],
        ]

        t1 = Table(data, colWidths=(None, 2 * cm, None))
        t1.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (0, 1), 0.25, colors.black),
                    ("INNERGRID", (2, 0), (2, 1), 0.25, colors.black),
                ]
            )
        )
        story.append(t1)

        return story

    @property
    def requisitions(self):
        """Returns a list of requisition model instances related
        to this appointment.
        """
        if not self._requisitions:
            for k, v in self.appointment.related_visit_model_cls().__dict__.items():
                try:
                    model_cls = getattr(getattr(v, "rel"), "related_model")
                except AttributeError:
                    pass
                else:
                    if issubclass(model_cls, RequisitionModelMixin):
                        self._requisitions.extend(
                            list(
                                getattr(self.appointment.related_visit, k).filter(
                                    clinic_verified=YES,
                                    panel__name__in=self.selected_panel_names,
                                )
                            )
                        )
        return self._requisitions

    @property
    def shipper_data(self):
        data = self.shipper.__dict__
        if self.contact_name.strip():
            data.update(contact_name=self.contact_name)
        return data

    @property
    def consignee_data(self):
        data = self.consignee.__dict__
        return data

    @staticmethod
    def formatted_address(**kwargs):
        data = {
            "contact_name": None,
            "name": None,
            "address": None,
            "city": None,
            "state": None,
            "postal_code": "0000",
            "country": None,
        }
        data.update(**kwargs)
        data_list = [
            v
            for v in [
                data.get("contact_name"),
                data.get("name"),
                data.get("address"),
                data.get("city")
                if not data.get("state")
                else "{} {}".format(data.get("city"), data.get("state")),
                data.get("postal_code"),
                data.get("country"),
            ]
            if v
        ]
        return "<br />".join(data_list)

    @property
    def description(self):
        return (
            "Please process the following specimens according to the "
            "panels listed below. Use the specimen identifier and "
            "subject identifier as a reference for panel results."
        )

    def append_requisition_items_story(self, story):
        story.append(Spacer(0.1 * cm, 0.5 * cm))
        index = 0
        for requisition in self.requisitions:
            table_data = []
            if index == 0:
                table_data.append(
                    [
                        Paragraph("BARCODE", self.styles["line_label_center"]),
                        Paragraph("ITEM", self.styles["line_label_center"]),
                        Paragraph("SPECIMEN", self.styles["line_label_center"]),
                        Paragraph("SUBJECT", self.styles["line_label_center"]),
                        Paragraph("PANEL", self.styles["line_label_center"]),
                        Paragraph("TYPE", self.styles["line_label_center"]),
                        Paragraph("DRAWN", self.styles["line_label_center"]),
                        Paragraph("RECV'D", self.styles["line_label_center"]),
                    ]
                )
            barcode = code39.Standard39(
                requisition.requisition_identifier, barHeight=10 * mm, stop=1
            )
            item_count = requisition.item_count or 1
            for count in range(1, item_count + 1):
                table_data.append(
                    [
                        barcode,
                        Paragraph(str(index + 1), self.styles["row_data"]),
                        Paragraph(
                            f"{requisition.human_readable_identifier} "
                            f"({count}/{item_count})",
                            self.styles["row_data"],
                        ),
                        Paragraph(
                            requisition.subject_identifier or "?",
                            self.styles["row_data"],
                        ),
                        Paragraph(
                            f"{requisition.panel_object.verbose_name} <br />"
                            f"({requisition.panel_object.abbreviation})",
                            self.styles["row_data"],
                        ),
                        Paragraph(
                            f"{requisition.panel_object.aliquot_type}",
                            self.styles["row_data"],
                        ),
                        Paragraph(
                            requisition.drawn_datetime.strftime("%Y-%m-%d"),
                            self.styles["row_data"],
                        ),
                        Paragraph("", self.styles["row_data"]),
                    ]
                )
                index += 1

            t1 = Table(table_data)
            t1.setStyle(
                TableStyle(
                    [
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                )
            )
            story.append(t1)

        return story
