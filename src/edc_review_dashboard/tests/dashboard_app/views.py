from edc_review_dashboard.views import SubjectReviewListboardView as Base
from edc_subject_dashboard.model_wrappers import SubjectVisitModelWrapper


class SubjectReviewListboardView(Base):

    listboard_model = "edc_model_admin.subjectvisit"
    model_wrapper_cls = SubjectVisitModelWrapper
    navbar_name = "edc_review_dashboard"

    search_form_url = "subject_review_listboard_url"

    def get_navbar_context_data(self, context):
        return context
