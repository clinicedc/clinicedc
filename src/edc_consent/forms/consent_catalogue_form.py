from edc.base.form.forms import BaseModelForm


class ConsentCatalogueForm (BaseModelForm):

    def clean(self, consent_instance=None):
        cleaned_data = self.cleaned_data
        return cleaned_data
