from django import forms
from django.test import TestCase

from adverse_event_app.models import AeFollowup
from edc_adverse_event.modelform_mixins import AeFollowupModelFormMixin


class TestModelformMixins(TestCase):
    def test_(self):
        class AeFollowupForm(AeFollowupModelFormMixin, forms.ModelForm):
            class Meta(AeFollowupModelFormMixin.Meta):
                model = AeFollowup
                fields = "__all__"
