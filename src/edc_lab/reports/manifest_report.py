from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_pdf_reports import Report
from reportlab.graphics.barcode import code39
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from ..models import Aliquot, Box, BoxItem
from ..site_labs import site_labs


class ManifestReportError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class ManifestReport(Report):
    def __init__(self, manifest=None, user=None, **kwargs):
        super().__init__(**kwargs)
        self.manifest = manifest  # a Manifest model instance
        self.user = user  # a User model instance
        self.box_model = Box
        self.box_item_model = BoxItem
        self.aliquot_model = Aliquot
        self.image_folder = mkdtemp()
        if self.manifest.shipped:
            self.report_filename = f"{self.manifest.manifest_identifier}.pdf"
        else:
            self.report_filename = "manifest_preview.pdf"

    def get_report_story(self, **kwargs):
        story = []

        data = [
            [
                Paragraph(
                    " ".join(self.manifest.site.name.split("_")).upper(),
                    self.styles["line_data_large"],
                )
            ],
            [Paragraph("SITE NAME", self.styles["line_label"])],
            [
                Paragraph(
                    self.formatted_address(**self.manifest.shipper.__dict__),
                    self.styles["line_data_large"],
                )
            ],
            [Paragraph("SITE DETAILS", self.styles["line_label"])],
        ]

        t = Table(data, colWidths=(9 * cm))
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (0, 1), 0.25, colors.black),
                    ("INNERGRID", (0, 2), (0, 3), 0.25, colors.black),
                ]
            )
        )
        t.hAlign = "RIGHT"

        story.append(t)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(
            Paragraph(
                "SPECIMEN MANIFEST{}".format(" (reprint)" if self.manifest.printed else ""),
                self.styles["line_label_center"],
            )
        )

        if self.manifest.shipped:
            barcode = code39.Standard39(
                self.manifest.manifest_identifier, barHeight=10 * mm, stop=1
            )
        else:
            barcode = "PREVIEW"

        data = [
            [
                Paragraph("MANIFEST NO.", self.styles["line_label"]),
                Paragraph(
                    (
                        self.manifest.human_readable_identifier
                        if self.manifest.shipped
                        else "PREVIEW"
                    ),
                    self.styles["line_data_largest"],
                ),
                barcode,
            ]
        ]
        t = Table(data, colWidths=(3 * cm, None, 5.5 * cm))
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (1, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(t)

        data = [
            [
                Paragraph("MANIFEST DATE", self.styles["line_label"]),
                Paragraph("EXPORT REFERENCES", self.styles["line_label"]),
            ],
            [
                Paragraph(
                    self.manifest.manifest_datetime.strftime("%Y-%m-%d"),
                    self.styles["line_data_largest"],
                ),
                Paragraph(
                    self.manifest.export_references or "",
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
                Paragraph(
                    "SHIPPER/EXPORTER (complete name and address)",
                    self.styles["line_label"],
                ),
                Paragraph("CONSIGNEE (complete name and address)", self.styles["line_label"]),
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

        data1 = [
            [
                Paragraph("COUNTRY OF EXPORT", self.styles["line_label"]),
                Paragraph(
                    "DESCRIPTION OF GOODS (description and special instructions)<br />",
                    self.styles["line_label"],
                ),
            ],
            [
                Paragraph(self.manifest.shipper.country, self.styles["line_data_largest"]),
                Paragraph(self.description, self.styles["line_data_large"]),
            ],
            [Paragraph("COUNTRY OF ORIGIN", self.styles["line_label"]), ""],
            [
                Paragraph(self.manifest.shipper.country, self.styles["line_data_largest"]),
                "",
            ],
            [
                Paragraph("COUNTRY OF ULTIMATE DESTINATION", self.styles["line_label"]),
                "",
            ],
            [
                Paragraph(self.manifest.consignee.country, self.styles["line_data_largest"]),
                "",
            ],
        ]
        t1 = Table(data1)
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
                            "I DECLARE THE INFORMATION CONTAINED IN THIS "
                            "MANIFEST TO BE TRUE AND CORRECT",
                            self.styles["line_label"],
                        )
                    ]
                ]
            )
        )

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        data1 = [
            [
                Paragraph(self.contact_name, self.styles["line_data_large"]),
                "",
                Paragraph(
                    self.manifest.export_datetime.strftime("%Y-%m-%d %H:%M")
                    if self.manifest.shipped
                    else "PREVIEW",
                    self.styles["line_data_large"],
                ),
            ],
            [
                Paragraph(
                    "SIGNATURE OF SHIPPER/EXPORTER (Type name and title and sign.)",
                    self.styles["line_label"],
                ),
                "",
                Paragraph("DATE", self.styles["line_label"]),
            ],
        ]

        t1 = Table(data1, colWidths=(None, 2 * cm, None))
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

        # boxes
        story.append(
            Table([[Paragraph("MANIFEST CONTENTS", self.styles["line_label_center"])]])
        )

        story = self.append_manifest_items_story(story)

        if self.manifest.shipped and not self.manifest.printed:
            self.manifest.printed = True
            self.manifest.save()

        return story

    @property
    def contact_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def shipper_data(self):
        data = self.manifest.shipper.__dict__
        if self.contact_name.strip():
            data.update(contact_name=self.contact_name)
        return data

    @property
    def consignee_data(self):
        data = self.manifest.consignee.__dict__
        return data

    def formatted_address(self, **kwargs):
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
        boxes = self.box_model.objects.filter(
            box_identifier__in=[obj.identifier for obj in self.manifest.manifestitem_set.all()]
        )
        box_items = self.box_item_model.objects.filter(box__in=boxes)
        aliquots = self.aliquot_model.objects.filter(
            aliquot_identifier__in=[obj.identifier for obj in box_items]
        )
        specimen_types = list(set([obj.aliquot_type for obj in aliquots]))
        description = {
            "box_count": boxes.count(),
            "specimen_count": aliquots.count(),
            "specimen_types": ", ".join(specimen_types),
        }
        box_word = "box" if boxes.count() == 1 else "boxes"
        specimen_word = "specimen" if aliquots.count() == 1 else "specimens"
        type_word = "type" if len(specimen_types) == 1 else "types"
        return (
            "{box_count} {box_word} containing {specimen_count} "
            "{specimen_word} of {type_word} {specimen_types}.".format(
                box_word=box_word,
                specimen_word=specimen_word,
                type_word=type_word,
                **description,
            )
        )

    def append_manifest_items_story(self, story):
        box_header = [
            Paragraph("BOX:", self.styles["line_label"]),
            Paragraph("CATEGORY:", self.styles["line_label"]),
            Paragraph("TYPES:", self.styles["line_label"]),
            Paragraph("ITEMS:", self.styles["line_label"]),
            Paragraph("BOX DATE:", self.styles["line_label"]),
            Paragraph("BOX BARCODE:", self.styles["line_label"]),
        ]
        for index, manifest_item in enumerate(
            self.manifest.manifestitem_set.all().order_by("-created")
        ):
            if index > 0:
                story.append(Spacer(0.1 * cm, 0.5 * cm))
            data1 = []
            data1.append(box_header)
            try:
                box = self.box_model.objects.get(box_identifier=manifest_item.identifier)
            except ObjectDoesNotExist as e:
                raise ManifestReportError(
                    f"{e} Got Manifest item '{manifest_item.identifier}'.",
                    code="unboxed_item",
                ) from e
            barcode = code39.Standard39(box.box_identifier, barHeight=5 * mm, stop=1)
            data1.append(
                [
                    Paragraph(box.box_identifier, self.styles["line_data_large"]),
                    Paragraph(
                        box.get_category_display().upper(),
                        self.styles["line_data_large"],
                    ),
                    Paragraph(box.specimen_types, self.styles["line_data_large"]),
                    Paragraph(
                        f"{str(box.count)}/{str(box.box_type.total)}",
                        self.styles["line_data_large"],
                    ),
                    Paragraph(
                        box.box_datetime.strftime("%Y-%m-%d"),
                        self.styles["line_data_large"],
                    ),
                    barcode,
                ]
            )
            t1 = Table(data1, colWidths=(None, None, None, None, None, None))
            t1.setStyle(
                TableStyle(
                    [
                        ("INNERGRID", (0, 0), (-1, 0), 0.25, colors.black),
                        ("INNERGRID", (0, 1), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                )
            )
            story.append(t1)
            story.append(Spacer(0.1 * cm, 0.5 * cm))

            table_data = []
            table_data = [
                [
                    Paragraph("BARCODE", self.styles["line_label_center"]),
                    Paragraph("POS", self.styles["line_label_center"]),
                    Paragraph("ALIQUOT IDENTIFIER", self.styles["line_label_center"]),
                    Paragraph("SUBJECT", self.styles["line_label_center"]),
                    Paragraph("TYPE", self.styles["line_label_center"]),
                    Paragraph("DATE", self.styles["line_label_center"]),
                ]
            ]
            for box_item in box.boxitem_set.all().order_by("position"):
                aliquot = self.get_aliquot(box_item.identifier)
                panel_object = self.get_panel_object(aliquot)
                barcode = code39.Standard39(
                    aliquot.aliquot_identifier, barHeight=5 * mm, stop=1
                )
                table_data.append(
                    [
                        barcode,
                        Paragraph(str(box_item.position), self.styles["row_data"]),
                        Paragraph(aliquot.human_readable_identifier, self.styles["row_data"]),
                        Paragraph(aliquot.subject_identifier, self.styles["row_data"]),
                        Paragraph(
                            "{} ({}) {}".format(
                                aliquot.aliquot_type,
                                aliquot.numeric_code,
                                panel_object.abbreviation,
                            ),
                            self.styles["row_data"],
                        ),
                        Paragraph(
                            aliquot.aliquot_datetime.strftime("%Y-%m-%d"),
                            self.styles["row_data"],
                        ),
                    ]
                )
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

    def get_aliquot(self, box_item_identifier=None):
        """Returns the aliquot instance for this box item."""
        try:
            aliquot = self.aliquot_model.objects.get(aliquot_identifier=box_item_identifier)
        except ObjectDoesNotExist as e:
            raise ManifestReportError(
                f"{e} Got Box item '{box_item_identifier}'",
                code="invalid_aliquot_identifier",
            )
        return aliquot

    def get_panel_object(self, aliquot=None):
        """Returns the panel object associated with this
        aliquot.
        """
        requisition = None
        for requisition_model in site_labs.requisition_models:
            model_cls = django_apps.get_model(requisition_model)
            try:
                requisition = model_cls.objects.get(
                    requisition_identifier=aliquot.requisition_identifier
                )
            except ObjectDoesNotExist:
                pass
        if not requisition:
            raise ManifestReportError(
                f"Invalid requisition identifier. Got {aliquot.requisition_identifier}",
                code="invalid_requisition_identifier",
            )
        return requisition.panel_object
