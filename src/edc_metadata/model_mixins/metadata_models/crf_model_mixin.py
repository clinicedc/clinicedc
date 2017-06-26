from django.apps import apps as django_apps

from .model_mixin import ModelMixin


class CrfModelMixin(ModelMixin):

    def __str__(self):
        return (f'CrfMeta {self.model}.{self.visit_code} {self.entry_status} '
                f'{self.subject_identifier}')

    @property
    def verbose_name(self):
        model = django_apps.get_model(self.model)
        return model._meta.verbose_name

    class Meta(ModelMixin.Meta):
        abstract = True
        verbose_name = "Crf Metadata"
        verbose_name_plural = "Crf Metadata"
        unique_together = (('subject_identifier', 'visit_schedule_name',
                            'schedule_name', 'visit_code', 'model'), )
