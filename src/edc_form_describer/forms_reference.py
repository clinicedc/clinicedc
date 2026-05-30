from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

from django.apps import apps as django_apps
from django.conf import settings
from django.utils import timezone

from .form_describer import FormDescriber
from .markdown_writer import MarkdownWriter


class FormsReferenceError(Exception):
    pass


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
        if admin_site is None:
            raise FormsReferenceError("admin_site is required")
        self.toc = []
        self.title = title or "Forms Reference"
        self._anchors: set[str] = set()
        self._markdown = []
        self.visit_schedules = visit_schedules or []
        self.admin_site = admin_site
        self.include_hidden_fields = include_hidden_fields
        self.plans = {}
        self.add_per_form_timestamp = (
            True if add_per_form_timestamp is None else add_per_form_timestamp
        )
        self.timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        self.flat = not self.visit_schedules
        for visit_schedule in self.visit_schedules:
            self.plans[visit_schedule.name] = {}
            for schedule in visit_schedule.schedules.values():
                for visit_code, visit in schedule.visits.items():
                    crfs = [(c.model, bool(c.required)) for c in visit.crfs]
                    requisitions = [r.panel.name for r in visit.requisitions]
                    self.plans[visit_schedule.name][visit_code] = {
                        "crfs": crfs,
                        "requisitions": requisitions,
                    }

    def to_file(
        self,
        path: Path | str | None = None,
        overwrite: bool | None = None,
        pad: int | None = None,
    ):
        pad = pad if pad is not None else 2
        markdown_writer = self.markdown_writer_cls(path=path, overwrite=overwrite)
        markdown_writer.to_file(markdown=self.markdown, pad=pad)

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
                self._anchors.add(anchor)
                break
            index += 1
            anchor = anchor_orig + f"-{index}"
        return anchor

    @property
    def markdown(self):
        if not self._markdown:
            if self.flat:
                self._markdown = self._build_flat_markdown()
            else:
                self._markdown = self._build_scheduled_markdown()
        return self._markdown

    # --- scheduled mode ---------------------------------------------------

    def _build_scheduled_markdown(self) -> list[str]:
        markdown: list[str] = []
        toc: list[str] = []
        for plan in self.plans.values():
            for visit_code, documents in plan.items():
                markdown.append(f"{self.h3} {visit_code}\n")
                toc.append(
                    f'\n<a href="#{self.anchor_prefix}-{visit_code.lower()}">'
                    f"**{visit_code}.**</a>"
                )
                crfs = documents.get("crfs") or []
                required_models = [m for m, req in crfs if req]
                optional_models = [m for m, req in crfs if not req]
                index = 0
                for model in required_models:
                    index = self._render_scheduled_crf(
                        model=model,
                        visit_code=visit_code,
                        index=index,
                        markdown=markdown,
                        toc=toc,
                    )
                if optional_models:
                    markdown.append(f"{self.h4} Optional forms\n")
                    for model in optional_models:
                        index = self._render_scheduled_crf(
                            model=model,
                            visit_code=visit_code,
                            index=index,
                            markdown=markdown,
                            toc=toc,
                        )
                requisitions = documents.get("requisitions") or []
                if requisitions:
                    markdown.append(f"{self.h4} Requisitions\n")
                    markdown.extend(
                        [f"* {panel_name}\n" for panel_name in requisitions]
                    )
        return self._finalize(markdown=markdown, toc=toc)

    def _render_scheduled_crf(
        self,
        model: str,
        visit_code: str,
        index: int,
        markdown: list[str],
        toc: list[str],
    ) -> int:
        model_cls = django_apps.get_model(model)
        admin_cls = self.admin_site._registry.get(model_cls)
        if not admin_cls:
            return index
        describer = self.describer_cls(
            admin_cls=admin_cls,
            include_hidden_fields=self.include_hidden_fields,
            visit_code=visit_code,
            level=self.h4,
            anchor_prefix=self.anchor_prefix,
            add_timestamp=self.add_per_form_timestamp,
        )
        if not describer.markdown:
            return index
        describer.markdown.append("\n")
        anchor = self.get_anchor(describer.anchor)
        toc.append(
            f'{index + 1}. <a href="#{anchor}">{describer.verbose_name}</a>'
        )
        markdown.extend(describer.markdown)
        return index + 1

    # --- flat mode --------------------------------------------------------

    def _build_flat_markdown(self) -> list[str]:
        markdown: list[str] = []
        toc: list[str] = []
        registry = sorted(
            self.admin_site._registry.items(),
            key=lambda kv: kv[0]._meta.verbose_name.lower(),
        )
        index = 0
        for model_cls, admin_cls in registry:
            describer = self.describer_cls(
                admin_cls=admin_cls,
                include_hidden_fields=self.include_hidden_fields,
                level=self.h3,
                anchor_prefix=self.anchor_prefix,
                add_timestamp=self.add_per_form_timestamp,
            )
            if not describer.markdown:
                continue
            describer.markdown.append("\n")
            anchor = self.get_anchor(describer.anchor)
            toc.append(
                f'{index + 1}. <a href="#{anchor}">{describer.verbose_name}</a>'
            )
            markdown.extend(describer.markdown)
            index += 1
        return self._finalize(markdown=markdown, toc=toc)

    # --- shared footer ----------------------------------------------------

    def _finalize(self, markdown: list[str], toc: list[str]) -> list[str]:
        markdown = self.insert_toc(toc, markdown)
        markdown.insert(0, f"{self.h1} {self.title}")
        markdown.append(
            f"\n\n*Version v{version(settings.APP_NAME)}* "
            f"*Rendered on {self.timestamp}*\n"
        )
        return markdown
