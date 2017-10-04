from .model_to_dataframe import ModelToDataframe


class SubjectModelToDataframe(ModelToDataframe):

    columns = {k: k for k in ['subject_identifier', 'gender', 'dob']}

    def __init__(self, columns=None, **kwargs):
        if columns:
            self.columns = {k: k for k in columns}
        super().__init__(**kwargs)
