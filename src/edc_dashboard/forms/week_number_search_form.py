from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms


class WeekNumberSearchForm(forms.Form):

    date_start = forms.IntegerField(
        # max_length=2,
        label="Start Week Number",
        help_text="Format is WW",
        error_messages={'required': 'Please enter a valid week number to start (0-52).'},
        validators=[MinValueValidator(1), MaxValueValidator(52), ],
        initial=date.today().isocalendar()[1])

    date_end = forms.IntegerField(
        # max_length=2,
        label="End Week Number",
        help_text="Format is WW",
        error_messages={'required': 'Please enter a valid week number to end (0-52).'},
        validators=[MinValueValidator(1), MaxValueValidator(52), ],
        initial=date.today().isocalendar()[1])

    year = forms.IntegerField(
        # max_length=4,
        label="Year",
        help_text="Format is YYYY",
        error_messages={'required': 'Please enter a valid year.'},
        initial=date.today().isocalendar()[0])

    def help_text(self):
        return "Enter a week number range (0-52) and the year"
