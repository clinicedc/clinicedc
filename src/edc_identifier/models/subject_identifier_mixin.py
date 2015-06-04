import re

from django.core.urlresolvers import reverse

from ..exceptions import IdentifierError


class SubjectIdentifierMixin(object):

    def save(self, *args, **kwargs):
        """Confirms subject_identifier is either a temporary uuid or
        an identifier and not a duplicate.

        Note: subject_identifier field is not always unique. See edc-consent."""
        using = kwargs.get('using')
        if not self.subject_identifier_as_pk:
            raise ValueError('Field subject_identifier_as_pk may not be blank')
        elif not self.subject_identifier:
            self.subject_identifier = str(self.subject_identifier_as_pk)
        elif self.__class__.objects.using(using).filter(
                subject_identifier=self.subject_identifier).exclude(pk=self.pk):
            raise IdentifierError(
                'Attempt to insert duplicate subject_identifier. Got \'{0}\' '
                'for subject_identifier_as_pk=\'{1}\'.'.format(
                    self.subject_identifier, self.subject_identifier_as_pk))
        super(SubjectIdentifierMixin, self).save(*args, **kwargs)

    def __str__(self):
        return self.mask_unset_subject_identifier()

    def mask_unset_subject_identifier(self):
        pattern = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        if pattern.match(str(self.subject_identifier)):
            return '<identifier not set>'
        return self.subject_identifier

    def dashboard(self):
        ret = None
        if self.subject_identifier:
            url = reverse('subject_dashboard_url', kwargs={
                'dashboard_type': self.subject_type.lower(),
                'dashboard_id': self.pk,
                'dashboard_model': 'registered_subject',
                'show': 'appointments'})
            ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        return ret
    dashboard.allow_tags = True
