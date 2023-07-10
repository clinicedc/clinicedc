from __future__ import annotations

import re
import string
import sys
from datetime import datetime
from math import floor
from typing import Optional

from django.core.management.color import color_style
from edc_fieldsets import Fieldsets
from edc_model.constants import DEFAULT_BASE_FIELDS

from .markdown_writer import MarkdownWriter

style = color_style()


class FormDescriberError(Exception):
    pass


class FormDescriber:

    """A class that prepares form reference information in
    markdown text.

    Usage:
        describer = FormDescriber(
                admin_cls=MyModelAdmin,
                include_hidden_fields=True)

        # get the markdown text as a list of lines
        markdown_lines = describer.markdown

        # get the markdown as text
        markdown = describer.to_markdown(title='Forms', add_timestamp=True)

        # or write markdown text directly to file
        describer.to_file(path=path, title='Forms', add_timestamp=True)

    """

    markdown_writer_cls = MarkdownWriter
    anchor_prefix = "user-content"
    level = "###"

    def __init__(
        self,
        admin_cls=None,
        include_hidden_fields=None,
        visit_code=None,
        level=None,
        anchor_prefix=None,
        add_timestamp=None,
    ):
        self._anchors = []
        self.markdown = []
        add_timestamp = True if add_timestamp is None else add_timestamp
        self.anchor_prefix = anchor_prefix or self.anchor_prefix
        timestamp = datetime.today().strftime("%Y-%m-%d %H:%M")
        self.level = level or self.level
        self.conditional_fieldset = None
        self.admin_cls = admin_cls
        self.model_cls = admin_cls.form._meta.model
        self.visit_code = visit_code
        self.models_fields = {fld.name: fld for fld in self.model_cls._meta.get_fields()}

        # include custom labels from admin
        try:
            self.custom_form_labels = {
                k: v
                for k, v in [
                    (form_label.field, form_label.label)
                    for form_label in self.admin_cls.custom_form_labels
                ]
            }
        except AttributeError:
            self.custom_form_labels = {}

        # include custom fieldsets from admin if visit_code
        self.fieldsets = self.admin_cls.fieldsets
        if not self.fieldsets:
            sys.stdout.write(
                style.ERROR(f"Warning: {admin_cls} has no fieldsets, skipping.\n")
            )
        else:
            try:
                self.conditional_fieldset = self.admin_cls.conditional_fieldsets.get(
                    self.visit_code
                )
            except AttributeError:
                self.conditional_fieldset = None
            else:
                if self.conditional_fieldset:
                    fieldsets = Fieldsets(self.admin_cls.fieldsets)
                    fieldsets.add_fieldsets(fieldsets=self.conditional_fieldset)
                    self.fieldsets = fieldsets.fieldsets
            if include_hidden_fields:
                self.add_hidden_fields()
            if add_timestamp:
                self.markdown.append(f"\n\n*Rendered on {timestamp}*\n")
            self.describe()

    @property
    def verbose_name(self):
        verbose_name = self.model_cls._meta.verbose_name
        if self.visit_code and self.conditional_fieldset:
            verbose_name = f"{verbose_name} ({self.visit_code})"
        return verbose_name.title()

    @property
    def anchor(self):
        allow = string.ascii_letters + string.digits + "-"
        slug = self.verbose_name.lower().replace(" ", "-")
        slug = re.sub("[^%s]" % allow, "", slug)
        return f"{self.anchor_prefix}-{slug}"

    def describe(self):
        """Appends all form features to a list `lines`."""
        number = 0.0
        self.markdown.append(f"{self.level} {self.verbose_name}")
        docstring = self.model_cls.__doc__
        if docstring.lower().startswith(self.model_cls._meta.label_lower.split(".")[1]):
            self.markdown.append("*[missing model class docstring]*\n\n")
        else:
            self.markdown.append(self.model_cls.__doc__)
        self.markdown.append(f"*Instructions*: {self.admin_cls.instructions}\n")
        if self.admin_cls.additional_instructions:
            self.markdown.append(
                f"*Additional instructions*: {self.admin_cls.additional_instructions}\n"
            )

        for fieldset_name, fieldset in self.fieldsets:
            if fieldset_name not in ["Audit"]:
                fieldset_name = fieldset_name or "Main"
                self.markdown.append(f"\n**Section: {fieldset_name}**")
                if fieldset.get("classes") != "collapse":
                    for fname in fieldset.get("fields"):
                        if fname not in DEFAULT_BASE_FIELDS:
                            number = self.get_next_number(number, fname)
                            self.add_field(fname=fname, number=number)

    def to_markdown(self):
        markdown_writer = self.markdown_writer_cls()
        return markdown_writer.to_markdown(markdown=self.markdown)

    def to_file(self, path: Optional[str] = None, overwrite: Optional[bool] = None):
        markdown_writer = self.markdown_writer_cls(path=path, overwrite=overwrite)
        markdown_writer.to_file(markdown=self.markdown)

    def add_hidden_fields(self):
        self.markdown.append("\n**Hidden fields:**")
        self.add_field(fname="report_datetime")
        base_fields = DEFAULT_BASE_FIELDS
        base_fields.append("revision")
        base_fields.sort()
        for fname in base_fields:
            self.add_field(fname=fname)

    def add_field(self, fname: str | None = None, number: float | None = None) -> None:
        number = number or "@"
        field_cls = self.models_fields.get(fname)
        if not field_cls:
            raise FormDescriberError(f"Unknown field {fname}")
        self.markdown.append(f"\n**{number}.** {field_cls.verbose_name}")
        if field_cls.help_text:
            self.markdown.append(f"\n&nbsp;&nbsp;&nbsp;&nbsp; *{field_cls.help_text}*")
        if self.custom_form_labels.get(fname):
            self.markdown.append(f"* custom_prompt: *{self.custom_form_labels.get(fname)}*")
        self.markdown.append(f"- db_table: {self.model_cls._meta.db_table}")
        self.markdown.append(f"- column: {field_cls.name}")
        self.markdown.append(f"- type: {field_cls.get_internal_type()}")
        if field_cls.max_length:
            self.markdown.append(f"- length: {field_cls.max_length}")
        if field_cls.get_internal_type() == "DateField":
            self.markdown.append("- format: YYYY-MM-DD")
        if field_cls.get_internal_type() == "DateTimeField":
            self.markdown.append("- format: YYYY-MM-DD HH:MM:SS.sss (tz=UTC)")
        self.add_field_responses(field_cls=field_cls)
        self.markdown.append("---")

    def add_field_responses(self, field_cls=None):
        if field_cls.get_internal_type() == "CharField":
            if field_cls.choices:
                self.markdown.append("- responses:")
                for response in [f"`{tpl[0]}`: *{tpl[1]}*" for tpl in field_cls.choices]:
                    self.markdown.append(f"  - {response}")
            else:
                self.markdown.append("- responses: *free text*")
        elif field_cls.get_internal_type() == "ManyToManyField":
            self.markdown.append("- responses: *Select all that apply*")
            for obj in field_cls.related_model.objects.all().order_by("display_index"):
                self.markdown.append(f"  - `{obj.name}`: *{obj.display_name}*")

    @staticmethod
    def get_next_number(number: float | None = None, fname: str | None = None) -> float:
        if "_other" in fname:
            number += 0.1
        else:
            number = floor(number)
            number += 1.0
        return round(number, ndigits=1)
