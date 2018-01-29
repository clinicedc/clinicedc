from django.apps import apps as django_apps


class RequisitionPanelError(Exception):
    pass


class RequisitionPanelModelError(Exception):
    pass


class InvalidProcessingProfile(Exception):
    pass


class Names:

    def __init__(self, name=None, alpha_code=None):
        self.abbreviation = f'{name[0:2]}{name[-1:]}'.upper()
        title = ' '.join(name.split('_')).title()
        alpha_code = alpha_code or ''
        self.verbose_name = f'{title} {alpha_code} {self.abbreviation}'.replace(
            '  ', ' ')


class RequisitionPanel:

    """A panel class that contains processing profile instances.
    """

    names_cls = Names
    requisition_model = None  # set by lab profile.add_panel
    lab_profile_name = None  # set by lab profile.add_panel
    panel_model = 'edc_lab.panel'

    def __init__(self, name=None, aliquot_type=None, processing_profile=None,
                 verbose_name=None, abbreviation=None, **kwargs):
        self._panel_model_obj = None
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
    def panel_model_cls(self):
        return django_apps.get_model(self.panel_model)

    @property
    def panel_model_obj(self):
        """Returns the underlying panel model instance.
        """
        if not self._panel_model_obj:
            self._panel_model_obj = self.panel_model_cls.objects.get(
                name=self.name, lab_profile_name=self.lab_profile_name)
        return self._panel_model_obj

    @property
    def pk(self):
        """Returns the PK as a UUID() fo the underlying
        panel model instance.
        """
        return self.panel_model_obj.pk

    @property
    def requisition_model_cls(self):
        """Returns the requisition model associated with this
        panel by it's lab profile.
        """
        try:
            requisition_model_cls = django_apps.get_model(
                self.requisition_model)
        except (ValueError, AttributeError, LookupError):
            raise RequisitionPanelModelError(
                f'Invalid requisition model. Got {self.requisition_model}. '
                f'See {repr(self)} or the lab profile {self.lab_profile_name}.')
        return requisition_model_cls

    @property
    def numeric_code(self):
        return self.aliquot_type.numeric_code

    @property
    def alpha_code(self):
        return self.aliquot_type.alpha_code

# TODO: panel should have some relation to the interface, e.g. a mapping of test_code to test_code on interface
#       for example CD4% = cd4_perc or VL = AUVL, VL = PMH
