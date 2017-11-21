from edc_model_wrapper import ModelWrapper


class SubjectVisitModelWrapper(ModelWrapper):

    model = None
    next_url_name = 'dashboard_url'
    next_url_attrs = ['subject_identifier', 'appointment']

    @property
    def appointment(self):
        return str(self.object.appointment.id)
