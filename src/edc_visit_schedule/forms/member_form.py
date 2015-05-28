from django import forms


class MemberForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data
