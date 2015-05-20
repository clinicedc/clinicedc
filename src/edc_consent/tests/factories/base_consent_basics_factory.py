from edc.subject.subject.tests.factories import BaseSubjectFactory


class BaseConsentBasicsFactory(BaseSubjectFactory):
    ABSTRACT_FACTORY = True

    consent_reviewed = 'Yes'
    study_questions = 'Yes'
    assessment_score = 'Yes'
    consent_copy = 'Yes'
