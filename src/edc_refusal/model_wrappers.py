from edc_screening.utils import get_subject_screening_app_label
from edc_subject_model_wrappers import (
    SubjectRefusalModelWrapper as BaseRefusalModelWrapper,
)


class SubjectRefusalModelWrapper(BaseRefusalModelWrapper):
    model = "edc_refusal.subjectrefusal"

    @property
    def querystring(self):
        return (
            f"cancel={get_subject_screening_app_label()}:screening_listboard_url,"
            f"screening_identifier&{super().querystring}"
        )
