from edc_dashboard.view_mixins import (
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
)
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ..view_mixins import SubjectReviewListboardViewMixin


class SubjectReviewListboardView(
    EdcViewMixin,
    NavbarViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    SubjectReviewListboardViewMixin,
    BaseListboardView,
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
