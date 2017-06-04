from .get_model_cls import GetModelCls


class RequisitionPanelError(Exception):
    pass


class InvalidProcessingProfile(Exception):
    pass


class Names:

    def __init__(self, name=None, alpha_code=None):
        self.abbreviation = f'{name[0:2]}{name[-1:]}'.upper()
        title = ' '.join(name.split('_')).title()
        alpha_code = alpha_code or ''
        self.verbose_name = f'{title} {alpha_code} {self.abbreviation}'.replace('  ', ' ')


class RequisitionPanel:

    """A container class of processing profile instances.
    """

    names_cls = Names
    model_cls = GetModelCls

    def __init__(self, name=None, model=None, aliquot_type=None,
                 processing_profile=None,
                 verbose_name=None, abbreviation=None, **kwargs):
        self._get_model = self.model_cls(model=model).get_model
        self.aliquot_type = aliquot_type
        self.verbose_name = None
        self.name = name
        try:
            names = self.names_cls(
                name=name, alpha_code=self.aliquot_type.alpha_code, **kwargs)
        except AttributeError as e:
            raise RequisitionPanelError(f'{self}. Got {e}.')
        self.abbreviation = abbreviation or names.abbreviation
        self.verbose_name = verbose_name or names.verbose_name
        self.processing_profile = processing_profile
        if self.processing_profile:
            if self.aliquot_type != self.processing_profile.aliquot_type:
                raise InvalidProcessingProfile(
                    f'Invalid processing profile for panel \'{self}\'. '
                    f'Got processing profile \'{self.processing_profile}\'')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name}, {self.aliquot_type})'

    def __str__(self):
        return self.verbose_name or self.name

    @property
    def model(self):
        return self._get_model()

    @property
    def numeric_code(self):
        return self.aliquot_type.numeric_code

    @property
    def alpha_code(self):
        return self.aliquot_type.alpha_code
# TODO: panel should have some relation to the interface, e.g. a mapping of test_code to test_code on interface
#       for example CD4% = cd4_perc or VL = AUVL, VL = PMH
