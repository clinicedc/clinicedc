from edc_visit_schedule.visit import Crf, CrfCollection

crfs = CrfCollection(
    Crf(show_order=1, model="tests.crfone", required=True),
    Crf(show_order=2, model="tests.crftwo", required=True),
    Crf(show_order=3, model="tests.crfthree", required=True),
    Crf(show_order=4, model="tests.crffour", required=True),
    Crf(show_order=5, model="tests.crffive", required=True),
)
