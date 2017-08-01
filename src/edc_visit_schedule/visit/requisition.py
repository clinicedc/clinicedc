from .crf import Crf


class ScheduledRequisitionError(Exception):
    pass


class Panel:

    def __init__(self, name=None):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.__class__.__name__}(self.name)'


class Requisition(Crf):

    def __init__(self, panel=None, required=None, **kwargs):
        required = False if required is None else required
        super().__init__(required=required, **kwargs)
        try:
            panel.name
        except AttributeError:
            self.panel = Panel(panel)
        else:
            self.panel = panel

    def __repr__(self):
        return f'{self.__class__.__name__}({self.show_order}, {self.panel})'

    def __str__(self):
        required = 'Required' if self.required else ''
        return f'{self.panel.name} {required}'

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
