from edc_list_data import PreloadData

from .constants import FILL_ACROSS


list_data = {}

model_data = {
    'edc_lab.boxtype': [
        {'name': '9 x 9',
         'across': 9,
         'down': 9,
         'total': 81,
         'fill_order': FILL_ACROSS}
    ]
}

unique_field_data = {}

preload_data = PreloadData(
    list_data=list_data,
    model_data=model_data,
    unique_field_data=unique_field_data)
