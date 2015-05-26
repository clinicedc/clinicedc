from datetime import datetime

from django.core.exceptions import ImproperlyConfigured


class OffStudyMixin(object):

    def get_off_study_cls(self):
        """Returns the model class of the local apps off study form
        called by private method :func:`_get_off_study_cls`.

        .. note:: This method must be overridden in the local app.
                  For example, in module mpepu_infant.models add::

                    from off_study.mixins import OffStudyMixin
                    from infant_off_study import InfantOffStudy


                    class InfantOffStudyMixin(OffStudyMixin):

                        def get_off_study_cls(self):
                            return InfantOffStudy
        """
        raise ImproperlyConfigured(
            'Method must be overridden to return the model class of the off '
            'study ModelForm. Model {0}'.format(self._meta.object_name))

    def _get_off_study_cls(self):
        """Private method that returns the off study model class by
        calling overridable method :func:`get_off_study_cls`."""
        return self.get_off_study_cls()

    def is_off_study(self):
        """Returns True if the off-study form exists for this subject, otherwise False.

        Once consented, a subject must be deliberately taken "off study" using a model that
        is a subclass of :class:`off_study.models.BaseOffStudy`."""
        if 'get_subject_identifier' not in dir(self):
            raise ImproperlyConfigured(
                'OffStudyMixin expected method \'get_subject_identifier\' to '
                'exist on the base model class. Model {0}'.format(self._meta.object_name))
        if 'get_report_datetime' not in dir(self):
            raise ImproperlyConfigured(
                'OffStudyMixin expected method \'get_report_datetime\' to '
                'exist on the base model class. Model {0}'.format(self._meta.object_name))
        report_datetime = self.get_report_datetime()
        report_date = datetime(report_datetime.year, report_datetime.month, report_datetime.day)
        if self._get_off_study_cls():
            return self._get_off_study_cls().objects.filter(
                registered_subject__subject_identifier=self.get_subject_identifier(),
                offstudy_date__lt=report_date
            ).exists()
        return False
