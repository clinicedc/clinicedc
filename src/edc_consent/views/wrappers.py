from edc_dashboard.wrappers import ModelWrapper


class ConsentModelWrapper(ModelWrapper):

    def add_extra_attributes_after(self):
        super().add_extra_attributes_after()
        self.version = self.wrapped_object.version
        self.verbose_name = self.wrapped_object.verbose_name
        self.consent_datetime = self.wrapped_object.consent_datetime
