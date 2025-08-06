from django import forms
from edc_registration.models import RegisteredSubject

from ...models import Allocation, StockRequest


class StockRequestForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("subject_identifiers") and cleaned_data.get(
            "excluded_subject_identifiers"
        ):
            raise forms.ValidationError(
                "Cannot include and exclude subject identifiers in the same request."
            )

        self.clean_dates(cleaned_data)

        if cleaned_data.get("subject_identifiers") and cleaned_data.get("location"):
            subject_identifiers = cleaned_data.get("subject_identifiers").split("\n")
            subject_identifiers = [s.strip() for s in subject_identifiers]
            self.cleaned_data["subject_identifiers"] = "\n".join(subject_identifiers)
            if RegisteredSubject.objects.values("subject_identifier").filter(
                subject_identifier__in=subject_identifiers,
                site_id=cleaned_data.get("location").site_id,
            ).count() != len(subject_identifiers):
                raise forms.ValidationError(
                    {"subject_identifiers": "Not all subject identifiers are valid."}
                )
        if cleaned_data.get("excluded_subject_identifiers") and cleaned_data.get("location"):
            subject_identifiers = cleaned_data.get("excluded_subject_identifiers").split("\n")
            subject_identifiers = [s.strip() for s in subject_identifiers]
            self.cleaned_data["excluded_subject_identifiers"] = "\n".join(subject_identifiers)
            if RegisteredSubject.objects.values("subject_identifier").filter(
                subject_identifier__in=subject_identifiers,
                site_id=cleaned_data.get("location").site_id,
            ).count() != len(subject_identifiers):
                raise forms.ValidationError(
                    {"excluded_subject_identifiers": "Not all subject identifiers are valid."}
                )

        if (
            cleaned_data.get("container")
            and cleaned_data.get("containers_per_subject")
            and cleaned_data.get("containers_per_subject")
            > cleaned_data.get("container").max_per_subject
        ):
            raise forms.ValidationError(
                {
                    "containers_per_subject": (
                        f"May not exceed {cleaned_data.get('container').max_per_subject}. "
                        "See 'max per subject' for this container"
                    )
                }
            )

        if not self.instance.id and cleaned_data.get("cancel") == "CANCEL":
            raise forms.ValidationError("Leave this blank")
        elif cleaned_data.get("cancel") == "CANCEL":
            if Allocation.objects.filter(
                stock_request_item__stock_request=self.instance
            ).exists():
                raise forms.ValidationError(
                    "May not be cancelled. Stock has been allocated for this request"
                )
        return cleaned_data

    @staticmethod
    def clean_dates(cleaned_data):
        if (
            cleaned_data.get("request_datetime")
            and cleaned_data.get("cutoff_datetime")
            and cleaned_data.get("cutoff_datetime") < cleaned_data.get("request_datetime")
        ):
            raise forms.ValidationError(
                {"cutoff_datetime": "Invalid. Must after the request date"}
            )
        if (
            cleaned_data.get("request_datetime")
            and cleaned_data.get("cutoff_datetime")
            and cleaned_data.get("cutoff_datetime").date()
            == cleaned_data.get("request_datetime").date()
        ):
            raise forms.ValidationError(
                {"cutoff_datetime": "Invalid. Must be at least 1 day after the request date"}
            )
        if (
            cleaned_data.get("start_datetime")
            and cleaned_data.get("request_datetime")
            and cleaned_data.get("start_datetime").date()
            > cleaned_data.get("request_datetime").date()
        ):
            raise forms.ValidationError(
                {"start_datetime": "Invalid.  Must on or before the request date"}
            )
        if (
            cleaned_data.get("start_datetime")
            and cleaned_data.get("cutoff_datetime")
            and cleaned_data.get("start_datetime").date()
            >= cleaned_data.get("cutoff_datetime").date()
        ):
            raise forms.ValidationError(
                {"cutoff_datetime": "Invalid.  Must be at least 1 day after start date"}
            )

    class Meta:
        model = StockRequest
        fields = "__all__"
        help_text = {"request_identifier": "(read-only)"}
        widgets = {
            "request_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
