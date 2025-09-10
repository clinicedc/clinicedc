from edc_visit_schedule.visit import Crf, CrfCollection

crfs = CrfCollection(
    Crf(show_order=1, model="clinicedc_tests.crfone", required=True),
    Crf(show_order=2, model="clinicedc_tests.crftwo", required=True),
    Crf(show_order=3, model="clinicedc_tests.crfthree", required=True),
    Crf(show_order=4, model="clinicedc_tests.crffour", required=True),
    Crf(show_order=5, model="clinicedc_tests.crffive", required=True),
)
