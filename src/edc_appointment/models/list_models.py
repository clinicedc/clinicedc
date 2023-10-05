from django.utils.translation import gettext_lazy as _
from edc_list_data.model_mixins import ListModelMixin


class InfoSources(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = _("Information Source")
        verbose_name_plural = _("Information Sources")
