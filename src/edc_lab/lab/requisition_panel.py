

class RequisitionPanel:

    def __init__(self, name, aliquot_type=None,
                 verbose_name=None, processing_profile=None,
                 abbreviation=None):
        self.name = name
        self.abbreviation = abbreviation or '{}{}'.format(
            name[0:2], name[-1:]).upper()
        self.verbose_name = verbose_name or '{} {}'.format(
            ' '.join(name.split('_')).title(), aliquot_type.alpha_code)
        self.aliquot_type = aliquot_type
        self.processing_profile = processing_profile

    def __repr__(self):
        return '<RequisitionPanel({}, {})>'.format(self.name, self.aliquot_type)

    def __str__(self):
        return self.verbose_name

# TODO: panel should have some relation to the interface, e.g. a mapping of test_code to test_code on interface
#       for example CD4% = cd4_perc or VL = AUVL, VL = PMH
