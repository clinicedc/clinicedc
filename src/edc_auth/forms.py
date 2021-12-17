from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm as BaseForm
from django.utils.safestring import mark_safe
from edc_randomization.auth_objects import RANDO_UNBLINDED
from edc_randomization.blinding import (
    is_blinded_user,
    raise_if_prohibited_from_unblinded_rando_group,
)

from .models import UserProfile


class UserChangeForm(BaseForm):
    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get("first_name"):
            raise forms.ValidationError({"first_name": "Required"})
        if not self.cleaned_data.get("last_name"):
            raise forms.ValidationError({"last_name": "Required"})
        if not self.cleaned_data.get("email"):
            raise forms.ValidationError({"email": "Required"})
        qs = self.cleaned_data.get("groups")
        if qs and qs.count() > 0:
            raise_if_prohibited_from_unblinded_rando_group(self.instance.username, qs)
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        qs = self.cleaned_data.get("email_notifications")
        if qs and qs.count() > 0:
            if not settings.EMAIL_ENABLED:
                raise forms.ValidationError(
                    {
                        "email_notifications": "You may not choose an email "
                        "notification. Email is not enabled. "
                        "Contact your EDC administrator."
                    }
                )
        qs = self.cleaned_data.get("sms_notifications")
        if qs and qs.count() > 0:
            if not settings.TWILIO_ENABLED:
                raise forms.ValidationError(
                    {
                        "sms_notifications": "You may not choose an SMS "
                        "notification. SMS is not enabled. "
                        "Contact your EDC administrator."
                    }
                )
        qs = self.cleaned_data.get("roles")
        if qs and qs.count() > 0:
            for role in qs:
                if RANDO_UNBLINDED in [
                    obj.name for obj in role.groups.all()
                ] and is_blinded_user(self.instance.user.username):
                    raise forms.ValidationError(
                        {
                            "roles": mark_safe(
                                "This user is not unblinded and may not be assigned "
                                f"the role of <U>{role.name.title()}</U>."
                            )
                        }
                    )
        return cleaned_data

    class Meta:
        model = UserProfile
        fields = "__all__"
