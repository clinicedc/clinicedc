from .enrollment_cap import EnrollmentCap


class EnrollmentCapAlreadyExists(Exception):
    pass


class EnrollmentCapDoesNotExist(Exception):
    pass


class SubjectType:

    enrollment_cap_cls = EnrollmentCap

    def __init__(self, name=None, verbose_name=None, model=None):
        self.enrollment_caps = []
        self.name = name
        self.verbose_name = verbose_name
        self.model = model

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, model={self.model})'

    def __str__(self):
        return f'{self.name}.{self.model}'

    def add_enrollment_cap(self, study_site=None, max_subjects=None):
        if study_site in self.enrollment_caps:
            raise EnrollmentCapAlreadyExists(
                f'Enrollment cap for site {study_site} already exists. See {repr(self)}.')
        self.enrollment_caps.append(
            self.enrollment_cap_cls(
                model=self.model,
                subject_type_name=self.name,
                study_site=study_site,
                max_subjects=max_subjects))

    def fetch_count_or_raise(self, study_site=None):
        for enrollment_cap in self.enrollment_caps:
            if enrollment_cap.study_site == study_site:
                break
        if not enrollment_cap:
            raise EnrollmentCapDoesNotExist(
                f'Enrollment cap does not exist for study site = {study_site}')
        count = enrollment_cap.fetch_count_or_raise()
        return count, enrollment_cap.max_subjects
