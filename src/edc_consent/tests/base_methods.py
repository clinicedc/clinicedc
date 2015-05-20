from datetime import datetime

from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.core.bhp_variables.tests.factories import StudySiteFactory, StudySpecificFactory
from edc.testing.models import TestConsent

from .factories import ConsentCatalogueFactory


class BaseMethods(object):

    def create_study_variables(self):
        self.study_site = StudySiteFactory(site_code='10', site_name='TEST_SITE')
        self.study_specific = StudySpecificFactory()

    def prepare_consent_catalogue(self):
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        content_type_map = ContentTypeMap.objects.get(model__iexact='TestConsent')
        ConsentCatalogueFactory(content_type_map=content_type_map, add_for_app='bhp_base_test')

    def create_consent(self):
        subject_consent = TestConsent.objects.create(
            first_name='TEST',
            last_name='TESTER',
            user_provided_subject_identifier=None,
            initials='TT',
            identity='111111111',
            confirm_identity='111111111',
            identity_type='omang',
            dob=datetime(1990, 01, 01),
            is_dob_estimated='No',
            gender='M',
            subject_type='subject',
            consent_datetime=datetime.today(),
            study_site=self.study_site,
            may_store_samples='Yes')
        return subject_consent
