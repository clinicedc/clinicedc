

class Panel:

    def __init__(self, name, alpha_code, verbose_name=None,
                 processing_profile=None, test_codes=None, group=None):
        self.group = group
        self.name = name
        self.verbose_name = verbose_name
        self.aliquot_type = alpha_code
        self.test_codes = test_codes
        self.processing_profile = processing_profile

# TODO: panel should have some relation to the interface, e.g. a mapping of test_code to test_code on interface
#       for example CD4% = cd4_perc or VL = AUVL, VL = PMH
