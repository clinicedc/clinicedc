from .crf import Crf


class RequisitionError(Exception):
    pass


class ScheduledRequisitionError(Exception):
    pass


class Panel:

    def __init__(self, name=None, verbose_name=None, requisition_model=None):
        self.name = name
        self.verbose_name = verbose_name or name
        self.requisition_model = requisition_model

    def __str__(self):
        return self.verbose_name

    def __repr__(self):
        return f'{self.__class__.__name__}(name=\'{self.name}\')'


class Requisition(Crf):

    def __init__(self, panel=None, required=None, **kwargs):
        required = False if required is None else required
        self.panel = panel
        model = panel.requisition_model
        if not model:
            raise RequisitionError(
                f'Invalid requisition model. Got model=\'{model}\'. See {repr(panel)}. '
                f'Was the panel referred to by this schedule\'s requisition '
                f'registered with site_labs?')
        super().__init__(required=required, model=model, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.show_order}, {self.panel.name})'

    def __str__(self):
        required = 'Required' if self.required else ''
        return f'{self.panel.name} {required}'

    @property
    def verbose_name(self):
        return self.panel.verbose_name

    def validate(self):
        """Raises an exception if a Requisition model lookup fails
        or if a panel is referred to that is not known to any
        lab_profiles

        See also: edc_lab.
        """
        super().validate()
        from edc_lab.site_labs import site_labs
        for lab_profile in site_labs.registry.values():
            if self.panel.name not in lab_profile.panels:
                raise ScheduledRequisitionError(
                    f'Panel does not exist in lab profiles. '
                    f'Got {repr(self.panel)}')
