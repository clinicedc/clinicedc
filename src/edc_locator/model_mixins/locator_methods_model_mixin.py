from django.db import models


class LocatorMethodsModelMixin(models.Model):
    @property
    def call(self):
        return self.may_call

    @property
    def call_work(self):
        return self.may_call_work

    @property
    def visit_home(self):
        return self.may_visit_home

    @property
    def sms(self):
        return self.may_sms

    @property
    def contact_indirectly(self):
        return self.may_contact_indirectly

    class Meta:
        abstract = True
