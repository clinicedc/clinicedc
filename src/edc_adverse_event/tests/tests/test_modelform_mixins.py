from django import forms
from django.test import TestCase

from adverse_event_app.models import AeFollowup

from ...forms import AeFollowupModelFormMixin


class TestModelformMixins(TestCase):
    def test_(self):
        class AeFollowupForm(AeFollowupModelFormMixin, forms.ModelForm):
            class Meta:
                model = AeFollowup
                fields = "__all__"
