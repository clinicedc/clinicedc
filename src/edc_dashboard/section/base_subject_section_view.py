# from django.views.base import View  # for 1.5
from .base_section_view import BaseSectionView


# class Section(View):  # 1.5
class BaseSubjectSectionView(BaseSectionView):

    dashboard_url_name = None

    def __init__(self):
        super(BaseSubjectSectionView, self).__init__()
        self._dashboard_url_name = None

    def set_dashboard_url_name(self, value=None):
        """Sets the _dashboard_url_name for this section."""
        if self.dashboard_url_name:  # try for class attribute first
            self._dashboard_url_name = self.dashboard_url_name
        else:
            self._section_name = value
        if not self._dashboard_url_name:
            raise TypeError('Attribute _dashboard_url_name may not be None for {0}'.format(self))

    def get_dashboard_url_name(self):
        """Returns the _dashboard_url_name for this section."""
        if not self._dashboard_url_name:
            self.set_dashboard_url_name()
        return self._dashboard_url_name

    def _contribute_to_context(self, context, request, *args, **kwargs):
        """Adds subject_dashboard_url to the context.

        .. note:: Overriding this method instead of :func:`contribute_to_context` so that users of the
                  class won't need to call super when overriding :func:`contribute_to_context`."""
        context = super(BaseSubjectSectionView, self)._contribute_to_context(context, request, *args, **kwargs)
        context.update({'subject_dashboard_url': self.get_dashboard_url_name()})
        return context
