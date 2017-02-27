from .base_identifier import Identifier


class BoxIdentifier(Identifier):

    random_string_length = 9
    identifier_attr = 'box_identifier'
    template = 'B{device_id}{random_string}'
