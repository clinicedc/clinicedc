from edc.base.modeladmin.admin import BaseModelAdmin
from edc.subject.consent.models import BaseConsent


class BaseConsentUpdateModelAdmin(BaseModelAdmin):

    def __init__(self, *args, **kwargs):
        self.list_display = [self.consent_name, 'consent_version', 'consent_datetime', 'created', 'user_created']
        super(BaseConsentUpdateModelAdmin, self).__init__(*args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == self.consent_name:
            kwargs["queryset"] = self.consent_model.objects.filter(pk=request.GET.get(db_field.name, None))
        super(BaseConsentUpdateModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        