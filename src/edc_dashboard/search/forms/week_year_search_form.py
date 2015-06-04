from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms


class WeekYearSearchForm(forms.Form):
    week_start = forms.IntegerField(
        # max_length=2,
        label="Start Week",
        help_text="Format is WW",
        error_messages={'required': 'Please enter a valid week number to start (0-52).'},
        validators=[MinValueValidator(1), MaxValueValidator(52), ],
        initial=date.today().isocalendar()[1]
    )

    year_start = forms.IntegerField(
        # max_length=4,
        label="Year",
        help_text="Format is YYYY",
        error_messages={'required': 'Please enter a valid year.'},
        initial=date.today().isocalendar()[0]
    )

    week_end = forms.IntegerField(
        # max_length=2,
        label="End Week",
        help_text="Format is WW",
        error_messages={'required': 'Please enter a valid week number to end (0-52).'},
        validators=[MinValueValidator(1), MaxValueValidator(52), ],
        initial=date.today().isocalendar()[1]
    )

    year_end = forms.IntegerField(
        # max_length=4,
        label="Year",
        help_text="Format is YYYY",
        error_messages={'required': 'Please enter a valid year.'},
        initial=date.today().isocalendar()[0]
    )

    def help_text(self):
        return "Enter a week number range (0-52) and the year"

    def clean(self):

        cleaned_data = self.cleaned_data

        my_year_start = cleaned_data.get("year_start")
        my_year_end = cleaned_data.get("year_end")
        my_week_start = cleaned_data.get("date_start")
        my_week_end = cleaned_data.get("date_end")

        if my_year_start > my_year_end:
            raise ValidationError(
                'Ensure \'End Year\' is greater than or equal to the \'Start Year\'. '
                'You wrote %s for \'End Year\'' % (my_year_end))
        if my_year_start == my_year_end and my_week_start > my_week_end:
            raise ValidationError(
                'Ensure \'End Week\' is greater than or equal to the \'Start Week\' '
                'for year %s. You wrote %s for \'End Week\'' % (my_year_end, my_week_end))
        return self.cleaned_data
