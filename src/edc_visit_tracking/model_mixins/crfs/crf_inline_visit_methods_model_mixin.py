from django.db import models


class CrfInlineVisitMethodsModelMixin(models.Model):

    @property
    def visit_code(self):
        return self.visit.visit_code

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier

    class Meta:
        abstract = True

# class ModelMixin(models.Model):
#
#     @classmethod
#     def visit_model(cls):
#         app_config = django_apps.get_app_config('edc_visit_tracking')
#         return app_config.visit_model(cls._meta.app_label)
#
#     @property
#     def visit_code(self):
#         return self.visit.visit_code
#
#     @property
#     def subject_identifier(self):
#         return self.visit.subject_identifier
#
#     class Meta:
#         abstract = True
