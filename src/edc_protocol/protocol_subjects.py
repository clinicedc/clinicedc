from django.conf import settings

if settings.APP_NAME == 'edc_protocol':

    from .constants import ALL_SITES
    from .subject_type import SubjectType
    from .site_protocol_subjects import site_protocol_subjects

    subject = SubjectType(
        name='subject',
        verbose_name='Research Subjects',
        model='edc_protocol.enrollment')

    subject.add_enrollment_cap(study_site=ALL_SITES, max_subjects=5)

    site_protocol_subjects.register(subject)

    subject = SubjectType(
        name='subject',
        verbose_name='Research Subjects',
        model='edc_protocol.enrollmentthree')

    subject.add_enrollment_cap(study_site=ALL_SITES, max_subjects=999)

    site_protocol_subjects.register(subject)
