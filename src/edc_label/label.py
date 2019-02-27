from django.utils import timezone

from .label_template import LabelTemplate


class Label:

    """A class that prepares data for x copies of labels.
    """

    label_name = "label"
    label_template_cls = LabelTemplate
    label_template_name = None

    def __init__(self, label_template_name=None):
        if label_template_name:
            self.label_template_name = label_template_name
        self.messages = None
        self.label_template = self.label_template_cls(
            template_name=self.label_template_name
        )

    def __str__(self):
        return f"{self.label_template_name}."

    @property
    def label_context(self):
        return {}

    def render_as_zpl_data(self, copies=None, context=None):
        copies = copies or 1
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        zpl_data = []
        for i in range(copies, 0, -1):
            context = context or self.label_context
            context.update(
                {"label_count": i, "label_count_total": copies, "timestamp": timestamp}
            )
            zpl_data.append(self.label_template.render(context).encode("utf8"))
        zpl_data = b"".join(zpl_data)
        return zpl_data
