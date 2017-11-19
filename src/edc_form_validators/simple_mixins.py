from dateutil.relativedelta import relativedelta
from django import forms

from edc_constants.constants import YES, NO, UNKNOWN, NOT_APPLICABLE

comparison_phrase = {
    'gt': 'must be greater than',
    'gte': 'must be greater than or equal to',
    'lt': 'must be less than',
    'lte': 'must be less than or equal to',
    'ne': 'may not equal', }


class SimpleYesNoValidationMixin:

    def require_if_yes(self, yesno_field, required_field,
                       required_msg=None, not_required_msg=None):
        if (self.cleaned_data.get(yesno_field) in [NO, UNKNOWN]
                and self.cleaned_data.get(required_field)):
            raise forms.ValidationError({
                required_field: [
                    not_required_msg
                    or 'This field is not required based on previous answer.']})
        elif (self.cleaned_data.get(yesno_field) == YES
              and not self.cleaned_data.get(required_field)):
            raise forms.ValidationError({
                required_field: [
                    required_msg
                    or 'This field is required based on previous answer.']})


class SimpleApplicableByAgeValidatorMixin:

    def validate_applicable_by_age(self, field, op, age, dob,
                                   previous_visit_date, subject_identifier,
                                   errmsg=None):
        age_delta = relativedelta(previous_visit_date, dob)
        applicable = True
        if self.cleaned_data.get(field):
            applicable = self.get_applicable(op, age_delta, age)
        if not applicable and self.cleaned_data.get(field) != NOT_APPLICABLE:
            raise forms.ValidationError({
                field: [errmsg or (
                    'Not applicable. Age {phrase} {age}y at previous visit. '
                    'Got {subject_age}y').format(
                        phrase=comparison_phrase.get(op),
                        age=age, subject_age=age_delta.years)]})
        if applicable and self.cleaned_data.get(field) == NOT_APPLICABLE:
            raise forms.ValidationError({
                field: [errmsg or (
                    'Applicable. Age {phrase} {age}y at previous visit to '
                    'be "not applicable". Got {subject_age}y').format(
                        phrase=comparison_phrase.get(op),
                        age=age, subject_age=age_delta.years)]})

    def get_applicable(self, op, age_delta, age):
        applicable = False
        if op == 'gt' and age_delta.years > age:
            applicable = True
        elif op == 'gte' and age_delta.years >= age:
            applicable = True
        elif op == 'lt' and age_delta.years < age:
            applicable = True
        elif op == 'lte' and age_delta.years <= age:
            applicable = True
        elif op == 'ne' and age_delta.years != age:
            applicable = True
        elif op == 'eq' and age_delta.years == age:
            applicable = True
        return applicable


class SimpleDateFieldValidatorMixin:

    def validate_dates(self, field1=None, op=None, field2=None, errmsg=None,
                       verbose_name1=None, verbose_name2=None,
                       value1=None, value2=None):
        """Validate that date1 is greater than date2.
        """
        date1 = self.cleaned_data.get(field1, value1)
        date2 = self.cleaned_data.get(field2, value2)
        if not self.compare_dates(date1, op, date2):
            raise forms.ValidationError({
                field1: [errmsg or '{field1} {phrase} {field2}.'.format(
                    field1=verbose_name1 or field1 or date1,
                    phrase=comparison_phrase.get(op),
                    field2=verbose_name2 or field2 or date2)]})

    def compare_dates(self, date1, op, date2):
        ret = True
        if date1 and date2:
            ret = False
            if op == 'gt' and date1 > date2:
                ret = True
            elif op == 'gte' and date1 >= date2:
                ret = True
            elif op == 'lt' and date1 < date2:
                ret = True
            elif op == 'lte' and date1 <= date2:
                ret = True
            elif op == 'ne' and date1 != date2:
                ret = True
            elif op == 'eq' and date1 == date2:
                ret = True
        return ret
