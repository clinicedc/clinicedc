from typing import Optional

from django.utils import timezone

from .label_template import LabelTemplate


class Label:

    """A class that prepares data for x copies of labels."""

    label_name = "label"
    label_template_cls = LabelTemplate
    label_template_name = None

    def __init__(
        self,
        label_template_name: Optional[str] = None,
        static_files_path: Optional[str] = None,
    ):
        if label_template_name:
            self.label_template_name = label_template_name
        self.messages = None
        self.label_template = self.label_template_cls(
            template_name=self.label_template_name, static_files_path=static_files_path
        )

    def __str__(self):
        return f"{self.label_template_name}."

    @property
    def label_context(self):
        return {}

    def render_as_zpl_data(self, copies=None, context=None, encoding=None):
        copies = copies or 1
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        encoding = "utf8" if encoding is None else encoding
        zpl_data = []
        for i in range(copies, 0, -1):
            context = context or self.label_context
            context.update(
                {"label_count": i, "label_count_total": copies, "timestamp": timestamp}
            )
            zpl = self.label_template.render(context)
            if encoding:
                zpl = zpl.encode(encoding)
            zpl_data.append(zpl)
        return (b"" if encoding else "").join(zpl_data)
