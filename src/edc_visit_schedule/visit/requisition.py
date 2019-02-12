from .crf import Crf


class RequisitionError(Exception):
    pass


class RequisitionLookupError(Exception):
    pass


class ScheduledRequisitionError(Exception):
    pass


class Requisition(Crf):
    def __init__(self, panel=None, required=None, **kwargs):
        required = False if required is None else required
        self.panel = panel
        if not self.panel.requisition_model:
            raise RequisitionError(
                f"Invalid requisition model. Got None. "
                f"See {repr(panel)}. "
                f"Was the panel referred to by this schedule's requisition "
                f"added to a lab profile and registered with site_labs?"
            )
        super().__init__(
            required=required, model=self.panel.requisition_model, **kwargs
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.show_order}, {self.panel.name})"

    def __str__(self):
        required = "Required" if self.required else ""
        return f"{self.panel.name} {required}"

    @property
    def name(self):
        return self.panel.name

    @property
    def verbose_name(self):
        return self.panel.verbose_name

    def validate(self):
        """Raises an exception if a Requisition model lookup fails
        or if a panel is referred to that is not known to any
        lab_profiles

        See also: edc_lab.
        """
        from edc_lab.site_labs import site_labs

        try:
            self.panel.requisition_model_cls
        except LookupError as e:
            raise RequisitionLookupError(e) from e

        for lab_profile in site_labs.registry.values():
            if self.panel.name not in lab_profile.panels:
                raise ScheduledRequisitionError(
                    f"Panel does not exist in lab profiles. " f"Got {repr(self.panel)}"
                )
