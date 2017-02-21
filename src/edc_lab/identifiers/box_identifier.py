from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier


class BoxIdentifier(AlphanumericIdentifier):

    name = 'boxidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{5}$'
    seed = ['AAA', '00000']
