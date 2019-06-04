from django import forms
from django.conf import settings


class UserProfileForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        qs = self.cleaned_data.get("email_notifications")
        if qs and qs.count() > 0:
            if not settings.EMAIL_ENABLED:
                raise forms.ValidationError(
                    {
                        "email_notifications": "You may not choose an email notification. Email is not enabled. "
                        "Contact your EDC administrator."
                    }
                )
        qs = self.cleaned_data.get("sms_notifications")
        if qs and qs.count() > 0:
            if not settings.TWILIO_ENABLED:
                raise forms.ValidationError(
                    {
                        "sms_notifications": "You may not choose an SMS notification. SMS is not enabled. "
                        "Contact your EDC administrator."
                    }
                )
        return cleaned_data
