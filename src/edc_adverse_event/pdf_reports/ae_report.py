from textwrap import fill

import inflect
from edc_constants.constants import OTHER, YES
from edc_reports.crf_pdf_report import CrfPdfReport
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table
from reportlab.platypus.flowables import KeepTogether, Spacer

from edc_adverse_event.get_ae_model import get_ae_model

p = inflect.engine()


class AeReport(CrfPdfReport):

    model_attr = "ae_initial"

    def __init__(self, ae_initial=None, **kwargs):
        super().__init__(**kwargs)
        self.ae_initial = ae_initial

    @property
    def title(self):
        return f"ADVERSE EVENT REPORT FOR {self.ae_initial.subject_identifier}"

    def get_report_story(self, **kwargs):

        story = []

        self.draw_demographics(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))
        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self._draw_section_one_header(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self._draw_ae_overview(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self._draw_ae_descripion(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self._draw_ae_drug_relationship(story)

        self._draw_ae_cause(story)

        self._draw_ae_action_taken(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))
        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self._draw_section_two(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self._draw_audit_trail(story)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        self.draw_end_of_report(story)

        return story

    def _draw_section_one_header(self, story):
        t = Table([["Section 1: Initial AE Report"]], (18 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        story.append(t)
        t = Table([[f"Prepared by {self.get_user(self.ae_initial)}."]], (18 * cm))
        self.set_table_style(t)
        story.append(t)

    def _draw_ae_overview(self, story):
        # basics
        classification_text = fill(self.ae_initial.ae_classification.name, width=80)
        if self.ae_initial.ae_classification.name == OTHER:
            classification_text = fill(
                f"{classification_text}: {self.ae_initial.ae_classification_other}",
                width=80,
            )

        sae_reason = (
            fill(f": {self.ae_initial.sae_reason.name}", width=80)
            if self.ae_initial.sae == YES
            else ""
        )
        sae_text = f"{self.ae_initial.get_sae_display()}{sae_reason}"

        susar_reported = ""
        if self.ae_initial.susar == YES:
            susar_reported = (
                ": reported" if self.ae_initial.susar_reported == YES else ": not reported"
            )
        susar_text = f"{self.ae_initial.get_susar_display()}{susar_reported}"

        rows = [
            ["Reference:", self.ae_initial.identifier],
            [
                "Report date:",
                self.ae_initial.report_datetime.strftime("%Y-%m-%d %H:%M"),
            ],
            ["Awareness date:", self.ae_initial.ae_awareness_date.strftime("%Y-%m-%d")],
            ["Actual start date:", self.ae_initial.ae_start_date.strftime("%Y-%m-%d")],
            ["Classification:", classification_text],
            ["Severity:", self.ae_initial.get_ae_grade_display()],
            ["SAE:", sae_text],
            ["SUSAR:", susar_text],
        ]

        t = Table(rows, (4 * cm, 14 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        t.hAlign = "LEFT"
        story.append(t)

    def _draw_ae_descripion(self, story):

        self.draw_narrative(
            story, title="Description of AE:", text=self.ae_initial.ae_description
        )

    def _draw_ae_drug_relationship(self, story):
        # relationship
        rows = [
            [
                "Is the incident related to the patient involvement in the study?",
                self.ae_initial.get_ae_study_relation_possibility_display(),
            ],
            [
                "Relationship to study drug:",
                self.ae_initial.get_study_drug_relation_display(),
            ],
        ]
        t = Table(rows, (14 * cm, 4 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        story.append(t)

    def _draw_ae_cause(self, story):

        # cause (Part3)
        left_width = 40 if self.ae_initial.ae_cause == YES else 80
        rows = [
            fill(
                "Has a reason other than the specified study drug been "
                "identified as the cause of the event(s)?",
                width=left_width,
            )
        ]
        if self.ae_initial.ae_cause == YES:
            rows.append(
                fill(
                    f"{self.ae_initial.get_ae_cause_display()}: "
                    f"{self.ae_initial.ae_cause_other}",
                    width=65,
                )
            )
            table_dimensions = (7 * cm, 11 * cm)
        else:
            rows.append(self.ae_initial.get_ae_cause_display())
            table_dimensions = (14 * cm, 4 * cm)
        t = Table([rows], table_dimensions)
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        story.append(t)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

    def _draw_ae_action_taken(self, story):

        self.draw_narrative(
            story,
            title="Action taken for treatment of AE:",
            text=self.ae_initial.ae_treatment,
        )

        story.append(Spacer(0.1 * cm, 0.5 * cm))

    def _draw_section_two(self, story):
        t1 = Table([["Section 2: Follow-up Reports"]], (18 * cm))
        self.set_table_style(t1, bg_cmd=self.bg_cmd)
        total = self.ae_initial.ae_follow_ups.count()
        row_text = f"There {p.plural_verb('is', total)} {p.no('follow-up report', total)}."
        t2 = Table([[row_text]], (18 * cm))
        self.set_table_style(t2)
        story.append(KeepTogether([t1, t2]))

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        for index, obj in enumerate(self.ae_initial.ae_follow_ups):
            self._draw_followup_story(story, obj, index + 1, total)
            story.append(Spacer(0.1 * cm, 0.5 * cm))
            story.append(Spacer(0.1 * cm, 0.5 * cm))

    def _draw_audit_trail(self, story):
        s = self.styles["line_data_small"]
        t = Table(
            [
                [
                    Paragraph("Document", s),
                    Paragraph("Changed by", s),
                    Paragraph("Date", s),
                    Paragraph("Action", s),
                ]
            ],
            (3 * cm, 3 * cm, 3 * cm, 9 * cm),
        )
        self.set_table_style(t, bg_cmd=("BACKGROUND", (0, 0), (3, -1), colors.lightgrey))
        story.append(t)

        followups = self.ae_initial.ae_follow_ups.order_by("-created")
        index = followups.count()
        for followup in followups:
            qs = followup.history.filter(id=followup.id).order_by("-history_date")
            for obj in qs:
                username = obj.user_created if obj.history_type == "+" else obj.user_modified
                t = Table(
                    [
                        [
                            Paragraph(
                                f"{get_ae_model('aefollowup')._meta.verbose_name}: {index}",
                                s,
                            ),
                            Paragraph(username, s),
                            Paragraph(obj.modified.strftime("%Y-%m-%d %H:%M"), s),
                            Paragraph(fill(self.history_change_message(obj), width=60), s),
                        ]
                    ],
                    (3 * cm, 3 * cm, 3 * cm, 9 * cm),
                )
                self.set_table_style(t)
                story.append(t)
            index -= 1
        qs = (
            get_ae_model("aeinitial")
            .history.filter(id=self.ae_initial.id)
            .order_by("-history_date")
        )
        for obj in qs:
            username = obj.user_created if obj.history_type == "+" else obj.user_modified
            t = Table(
                [
                    [
                        Paragraph(get_ae_model("aeinitial")._meta.verbose_name, s),
                        Paragraph(username, s),
                        Paragraph(obj.modified.strftime("%Y-%m-%d %H:%M"), s),
                        Paragraph(fill(self.history_change_message(obj), width=60), s),
                    ]
                ],
                (3 * cm, 3 * cm, 3 * cm, 9 * cm),
            )
            self.set_table_style(t)
            story.append(t)

    def _draw_followup_story(self, story, obj, index, total):
        rows = [
            ["Reference:", obj.identifier],
            ["Report date:", obj.report_datetime.strftime("%Y-%m-%d %H:%M")],
            ["Outcome date:", obj.outcome_date.strftime("%Y-%m-%d")],
            ["Outcome:", obj.get_outcome_display()],
            ["Severity increase:", obj.get_ae_grade_display()],
            ["Follow-up pending:", obj.get_followup_display()],
        ]

        t = Table([[f"Follow-up Report {index}/{total}"]], (18 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        story.append(t)
        t = Table([[f"Prepared by {self.get_user(obj)}."]], (18 * cm))
        self.set_table_style(t)
        story.append(t)
        t = Table(rows, (4 * cm, 14 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        story.append(t)

        self.draw_narrative(
            story,
            title="Description of follow-up AE outcome:",
            text=obj.relevant_history,
        )
