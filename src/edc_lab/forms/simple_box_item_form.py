from django import forms


class SimpleBoxItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    class Meta:
        fields = '__all__'
