from datetime import date
from django import forms


class DateRangeSearchForm(forms.Form):
    date_start = forms.DateField(
        # max_length=10,
        label="Start Date",
        help_text="Format is YYYY-MM-DD",
        error_messages={'required': 'Please enter a valid date.'},
        initial=date.today()
    )

    date_end = forms.DateField(
        # max_length=10,
        label="End Date",
        help_text="Format is YYYY-MM-DD",
        error_messages={'required': 'Please enter a valid date.'},
        initial=date.today()
    )

    def help_text(self):
        return "Enter the start date and the end date for the period to be listed. Format is YYYY-MM-DD."
