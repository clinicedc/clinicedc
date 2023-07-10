from datetime import datetime
from typing import Optional

from django.apps import apps as django_apps

from .form_describer import FormDescriber
from .markdown_writer import MarkdownWriter


class FormsReference:
    describer_cls = FormDescriber
    markdown_writer_cls = MarkdownWriter
    anchor_prefix = "user-content"
    h1 = "#"
    h2 = "##"
    h3 = "###"
    h4 = "####"

    def __init__(
        self,
        visit_schedules=None,
        admin_site=None,
        include_hidden_fields=None,
        title=None,
        add_per_form_timestamp: bool | None = None,
    ):
        self.toc = []
        self.title = title or "Forms Reference"
        self._anchors = []
        self._markdown = []
        self.visit_schedules = visit_schedules
        self.admin_site = admin_site
        self.include_hidden_fields = include_hidden_fields
        self.plans = {}
        self.add_per_form_timestamp = (
            True if add_per_form_timestamp is None else add_per_form_timestamp
        )
        self.timestamp = datetime.today().strftime("%Y-%m-%d %H:%M")
        for visit_schedule in self.visit_schedules:
            self.plans.update({visit_schedule.name: {}})
            for schedule in visit_schedule.schedules.values():
                for visit_code, visit in schedule.visits.items():
                    crfs = []
                    requisitions = []
                    for c in visit.crfs:
                        crfs.append(c.model)
                    for r in visit.requisitions:
                        requisitions.append(r.panel.name)
                    self.plans[visit_schedule.name].update(
                        {visit_code: {"crfs": crfs, "requisitions": requisitions}}
                    )

    def to_file(self, path: Optional[str] = None, overwrite: Optional[bool] = None):
        markdown_writer = self.markdown_writer_cls(path=path, overwrite=overwrite)
        markdown_writer.to_file(markdown=self.markdown, pad=2)

    def insert_toc(self, toc=None, markdown=None):
        toc.reverse()
        markdown.insert(0, "\n")
        for line in toc:
            markdown.insert(0, line)
        markdown.insert(0, f"{self.h2} Table of contents\n")
        return markdown

    def get_anchor(self, anchor=None):
        index = 0
        anchor_orig = anchor
        while True:
            if anchor not in self._anchors:
                self._anchors.append(anchor)
                break
            else:
                index += 1
                anchor = anchor_orig + f"-{index}"
        return anchor

    @property
    def markdown(self):
        if not self._markdown:
            markdown = []
            toc = []
            for plan in self.plans.values():
                for visit_code, documents in plan.items():
                    markdown.append(f"{self.h3} {visit_code}\n")
                    toc.append(
                        f'\n<a href="#{self.anchor_prefix}-{visit_code.lower()}">'
                        f"**{visit_code}.**</a>"
                    )
                    for index, model in enumerate(documents.get("crfs")):
                        model_cls = django_apps.get_model(model)
                        admin_cls = self.admin_site._registry.get(model_cls)
                        describer = self.describer_cls(
                            admin_cls=admin_cls,
                            include_hidden_fields=self.include_hidden_fields,
                            visit_code=visit_code,
                            level=self.h4,
                            anchor_prefix=self.anchor_prefix,
                            add_timestamp=self.add_per_form_timestamp,
                        )
                        describer.markdown.append("\n")
                        anchor = f"{self.get_anchor(describer.anchor)}"
                        toc.append(
                            f'{index + 1}. <a href="#{anchor}">'
                            f"{describer.verbose_name}</a>"
                        )
                        markdown.extend(describer.markdown)
                    markdown.append(f"{self.h4} Requisitions\n")
                    for panel_name in documents.get("requisitions"):
                        markdown.append(f"* {panel_name}\n")
            markdown = self.insert_toc(toc, markdown)
            markdown.insert(0, f"{self.h1} {self.title}")
            markdown.append(f"\n\n*Rendered on {self.timestamp}*\n")
            self._markdown = markdown
        return self._markdown
