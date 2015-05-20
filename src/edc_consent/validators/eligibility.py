from django.core.exceptions import ValidationError


def eligible_if_yes(value):
    if value != 'Yes':
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_yes_or_declined(value):
    if value not in ['Yes', 'Declined']:
        raise ValidationError('Please provide the subject with a copy of the consent.')


def eligible_if_no(value):
    if value != 'No':
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_unknown(value):
    if value != 'Unknown':
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_female(value):
    if value != 'F':
        raise ValidationError('If gender not Female, Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_male(value):
    if value != 'M':
        raise ValidationError('If gender not Male, Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_negative(value):
    if value != 'NEG':
        raise ValidationError('Participant must be HIV Negative. Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_positive(value):
    if value != 'POS':
        raise ValidationError('Participant must be HIV Positive. Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_not_positive(value):
    if value == 'POS':
        raise ValidationError('Participant must be HIV Negative / Unknown. Participant is NOT ELIGIBLE and registration cannot continue.')
