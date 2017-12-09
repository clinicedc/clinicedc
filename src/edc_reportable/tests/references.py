from edc_constants.constants import FEMALE, MALE

from ..parsers import parse as p


age_opts = dict(
    age_lower=18,
    age_upper=120,
    age_units='years',
    age_lower_inclusive=True,
    age_upper_inclusive=True)

opts = dict(
    lower_inclusive=True,
    upper_inclusive=True)

normal_data = {
    'haemoglobin': [
        p('13.5<=x<=17.5', units='g/dL', gender=[MALE], **age_opts),
        p('12.0<=x<=15.5', units='g/dL', gender=[FEMALE], **age_opts)],
    'platelets': [
        p('150<=x<=450', units='10e9/L', gender=[MALE, FEMALE], **age_opts)],
    'neutrophils': [
        p('2.5<=x<=7.5', units='10e9/L', gender=[MALE, FEMALE], **age_opts)],
    'sodium': [
        p('135<=x<=145', units='mmol/L', gender=[MALE, FEMALE], **age_opts)],
    'potassium': [
        p('3.6<=x<=5.2', units='mmol/L', gender=[MALE, FEMALE], **age_opts)],
    'magnesium': [
        p('0.75<=x<=1.2', units='mmol/L', gender=[MALE, FEMALE], **age_opts)],
    'alt': [
        p('10<=x<=40', units='IU/L', gender=[MALE, FEMALE], **age_opts)],
    'creatinine': [
        p('0.6<=x<=1.3', units='mg/dL', gender=[MALE, FEMALE], **age_opts),
        p('53<=x<=115', units='umol/L', gender=[MALE, FEMALE], **age_opts)],
}

grading_data = {
    'haemoglobin': [
        p('7.0<=x<9.0', grade=3, units='g/dL', gender=[MALE], **age_opts),
        p('6.5<=x<8.5', grade=3, units='g/dL', gender=[FEMALE], **age_opts),
        p('x<7.0', grade=4, units='g/dL', gender=[MALE], **age_opts),
        p('x<6.5', grade=4, units='g/dL', gender=[FEMALE], **age_opts),
    ],
    'platelets': [
        p('25<=x<=50', grade=3, units='10e9/L',
          gender=[MALE, FEMALE], **age_opts),
        p('x<25', grade=4, units='10e9/L', gender=[MALE, FEMALE], **age_opts),
    ],
    'neutrophils': [
        p('0.4<=x<=0.59', grade=3, units='10e9/L',
          gender=[MALE, FEMALE], **age_opts),
        p('x<0.4', grade=3, units='10e9/L', gender=[MALE, FEMALE], **age_opts),
    ],
    'sodium': [
        p('121<=x<=124', grade=3, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('154<=x<=159', grade=3, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('160<=x', grade=4, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('x<=120', grade=4, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
    ],
    'potassium': [
        p('2.0<=x<=2.4', grade=3, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('6.5<=x<=7.0', grade=3, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('x<2.0', grade=4, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('7.0<x', grade=4, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
    ],
    'magnesium': [
        p('0.3<=x<=0.44', grade=3, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('0.3<x', grade=4, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
    ],
    'alt': [
        p('200<=x<=400', grade=3, units='IU/L',
          gender=[MALE, FEMALE], **age_opts),
        p('400<x', grade=4, units='IU/L',
          gender=[MALE, FEMALE], **age_opts),
    ],
    'creatinine': [
        p('2.47<=x<=4.42', grade=3, units='mg/dL',
          gender=[MALE, FEMALE], **age_opts),
        p('216<=x<=400', grade=3, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
        p('4.55<x', grade=4, units='mg/dL',
          gender=[MALE, FEMALE], **age_opts),
        p('400<x', grade=4, units='mmol/L',
          gender=[MALE, FEMALE], **age_opts),
    ],
}
