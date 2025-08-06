from edc_form_validators import FormValidator

INVALID_CLINIC_DAY = "INVALID_CLINIC_DAY"


class HealthFacilityFormValidator(FormValidator):
    def clean(self):
        mon = self.cleaned_data.get("mon")
        tue = self.cleaned_data.get("tue")
        wed = self.cleaned_data.get("wed")
        thu = self.cleaned_data.get("thu")
        fri = self.cleaned_data.get("fri")
        sat = self.cleaned_data.get("sat")
        sun = self.cleaned_data.get("sun")
        if not any([mon, tue, wed, thu, fri, sat, sun]):
            self.raise_validation_error(
                "Select at least one clinic day.", error_code=INVALID_CLINIC_DAY
            )
