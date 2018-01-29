
class SubjectScheduleModelFormMixin:

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
