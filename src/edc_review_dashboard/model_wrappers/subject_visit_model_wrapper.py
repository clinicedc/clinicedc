from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from edc_dashboard import url_names
from edc_subject_model_wrappers import SubjectVisitModelWrapper as Base


class SubjectVisitModelWrapper(Base):
    @property
    def subject_dashboard_href(self):
        kwargs = dict(
            subject_identifier=self.object.subject_identifier,
            appointment=str(self.object.appointment.pk),
        )
        try:
            url = reverse(url_names.get(self.get_next_url_name()), kwargs=kwargs)
        except NoReverseMatch as e:
            raise NoReverseMatch(
                f"{e}. Using url_name='{url_names.get(self.get_next_url_name())}',"
                f"kwargs={kwargs}.  See {repr(self)}."
            )
        return url
