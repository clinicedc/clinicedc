from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from .subject_review_listboard_view import SubjectReviewListboardView


class EdcSubjectReviewListboardView(
    EdcViewMixin,
    NavbarViewMixin,
    SubjectReviewListboardView,
):

    """
    Declare in your app:

        class SubjectReviewListboardView(Base):

            listboard_model = 'ambition_subject.subjectvisit'
            model_wrapper_cls = SubjectVisitModelWrapper
            navbar_name = 'ambition_dashboard'

    Add URLs:

        subject_listboard_url_config = UrlConfig(
            url_name='subject_listboard_url',
            view_class=SubjectListboardView,
            label='subject_listboard',
            identifier_label='subject_identifier',
            identifier_pattern=subject_identifier)
        urlpatterns += subject_review_listboard_url_config.listboard_urls

    """
    pass
