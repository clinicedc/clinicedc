class AliquotIdentifier:

    def __init__(self, parent_identifier=None, aliquot_type=None, count=None):
        prefix = parent_identifier[0:10]
        child_segment = parent_identifier[-4:]
        self.identifier = (
            prefix + child_segment
            + aliquot_type.numeric_code
            + '{0:02d}'.format(count))
