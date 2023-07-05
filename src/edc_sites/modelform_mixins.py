from django import forms


class SiteModelFormMixin:

    """Validate the current site against a form question.

    This should be used sparingly. A good place is on the screening and/or consent form.

    Declare the modeladmin class with `SiteModelAdminMixin` to have
    the current site set on the form from the request object.

    Declare a `site` field with widget on the ModeForm:

    site = SiteField()

    You will also need to re-declare the `site` model field as `editable`.
    """

    def clean(self) -> dict:
        cleaned_data = super().clean()
        self.validate_with_current_site(cleaned_data)
        return cleaned_data

    def validate_with_current_site(self, cleaned_data: dict) -> None:
        current_site = getattr(self, "current_site", None)
        if (
            current_site
            and cleaned_data.get("site")
            and current_site.id != cleaned_data.get("site").id
        ):
            raise forms.ValidationError(
                {
                    "site": (
                        "Invalid. Please check you are logged into the correct site "
                        "before continuing"
                    )
                }
            )
