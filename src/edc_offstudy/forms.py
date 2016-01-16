from django import forms


class OffStudyFormMixin(forms.ModelForm):

    """Used to edit the off study form and throws an exception
    if the off study date is invalid."""

    def clean(self):
        cleaned_data = super(OffStudyFormMixin, self).clean()
        self._meta.model(**cleaned_data).off_study_visit_exists_or_raise(
            exception_cls=forms.ValidationError)
        self.validate_offstudy_date()
        return cleaned_data

    def validate_offstudy_date(self):
        cleaned_data = self.cleaned_data
        try:
            subject_identifier = cleaned_data.get(
                'maternal_visit').appointment.registered_subject.subject_identifier
            consent = self._meta.model.consent_model.objects.get(
                registered_subject__subject_identifier=subject_identifier)
            try:
                if cleaned_data.get('offstudy_date') < consent.consent_datetime.date():
                    raise forms.ValidationError("Off study date cannot be before consent date")
                if cleaned_data.get('offstudy_date') < consent.dob:
                    raise forms.ValidationError("Off study date cannot be before dob")
            except AttributeError:
                pass
        except consent.DoesNotExist:
            raise forms.ValidationError('Maternal Consent does not exist.')

    class Meta:
        abstract = True
