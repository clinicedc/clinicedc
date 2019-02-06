from .crf_model_wrapper import CrfModelWrapper


class RequisitionModelWrapper(CrfModelWrapper):

    visit_model_attr = "subject_visit"

    querystring_attrs = [visit_model_attr, "panel"]

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(object={self.object} "
            f"id={self.object.id}, panel={self.panel})"
        )

    @property
    def panel(self):
        try:
            return str(self.object.panel.id)
        except AttributeError as e:
            return str(e)

    @property
    def panel_display_name(self):
        try:
            return str(self.object.panel.display_name)
        except AttributeError as e:
            return str(e)

    @property
    def html_id(self):
        return f"id_{self.panel}"
