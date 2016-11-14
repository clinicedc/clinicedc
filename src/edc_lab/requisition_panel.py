

class RequisitionPanel:

    def __init__(self, name, alpha_code, verbose_name=None, processing_profile=None):
        self.name = name
        self.verbose_name = verbose_name
        self.aliquot_type = alpha_code
        self.processing_profile = processing_profile
        self._alpha_code = alpha_code

    def __repr__(self):
        return '<RequisitionPanel({}, {})>'.format(self.name, self._alpha_code)

# TODO: panel should have some relation to the interface, e.g. a mapping of test_code to test_code on interface
#       for example CD4% = cd4_perc or VL = AUVL, VL = PMH
