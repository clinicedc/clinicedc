from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier


class ReceiveIdentifier(AlphanumericIdentifier):

    name = 'receiveidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']
