# import time
# from django.test import LiveServerTestCase
# from django.contrib.auth.models import User
# from selenium.webdriver.firefox.webdriver import WebDriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.keys import Keys
# from edc.subject.registration.models import RegisteredSubject
# from edc.testing.models import TestSubjectUuidModel, TestForeignKey, TestM2m
# from edc_consent import BaseMethods
# 
# 
# class SeleniumTests(LiveServerTestCase, BaseMethods):
# 
#     def setUp(self):
#         self.adminuser = User.objects.create_user('django', 'django@test.com', 'pass')
#         self.adminuser.save()
#         self.adminuser.is_staff = True
#         self.adminuser.is_active = True
#         self.adminuser.is_superuser = True
#         self.adminuser.save()
#         self.logged_in = False
#         self.login()
#         self.create_study_variables()
#         self.prepare_consent_catalogue()
#         TestM2m.objects.create(name='test_m2m1', short_name='test_m2m1')
#         TestM2m.objects.create(name='test_m2m2', short_name='test_m2m2')
#         TestM2m.objects.create(name='test_m2m3', short_name='test_m2m3')
#         TestForeignKey.objects.create(name='test_fk', short_name='test_fk')
# 
#     @classmethod
#     def setUpClass(cls):
#         cls.selenium = WebDriver()
#         super(SeleniumTests, cls).setUpClass()
# 
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super(SeleniumTests, cls).tearDownClass()
# 
#     def login(self):
#         self.selenium.get('%s%s' % (self.live_server_url, '/erik/'))
#         self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
#         username_input = self.selenium.find_element_by_name("username")
#         username_input.send_keys('django')
#         password_input = self.selenium.find_element_by_name("password")
#         password_input.send_keys('pass')
#         self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
#         self.selenium.get('%s%s' % (self.live_server_url, '/admin/testing'))
#         self.logged_in = True
# 
#     def test_test_model(self):
#         subject_consent = self.create_consent()
#         RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier)
#         self.selenium.find_element_by_xpath('//input[@value="Administration"]').click()
#         self.selenium.find_element_by_xpath('//input[@value="Site Admin"]').click()
#         self.selenium.find_element_by_xpath('//a[@href="/admin/edc_consent/testsubjectuuidmodel/add/"]').click()
#         WebDriverWait(self.selenium, 10).until(
#             lambda s: s.find_element_by_name("name"))
#         fld = self.selenium.find_element_by_name("name")
#         fld.send_keys('TEST')
#         fld = self.selenium.find_element_by_name("registered_subject")
#         fld.send_keys(Keys.ARROW_DOWN)
#         fld = self.selenium.find_element_by_name("test_foreign_key")
#         fld.send_keys(Keys.ARROW_DOWN)
#         fld = self.selenium.find_element_by_name("test_many_to_many")
#         fld.send_keys(Keys.ARROW_RIGHT)
#         fld.send_keys(Keys.ARROW_DOWN)
#         self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#         WebDriverWait(self.selenium, 10).until(
#             lambda s: 'model to change' in s.title, 'Expected to return to Site Administration after save()')
#         pk = TestSubjectUuidModel.objects.all()[0].pk
#         self.selenium.find_element_by_xpath('//a[@href="{0}/"]'.format(pk)).click()
#         self.assertIsNotNone(TestSubjectUuidModel.objects.get(pk=pk).test_many_to_many.all())
#         self.assertEqual([test_many_to_many.name for test_many_to_many in TestSubjectUuidModel.objects.get(pk=pk).test_many_to_many.all()], ['test_m2m2'])
#         # complete the edc_consent
# 
#         time.sleep(5)
