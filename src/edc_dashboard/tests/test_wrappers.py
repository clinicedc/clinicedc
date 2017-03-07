from django.test import TestCase, tag

from edc_base_test.utils import get_utcnow
from edc_example.models import Example, ExampleLog, ExampleLogEntry, ParentExample

from ..wrappers import ModelWrapper, ModelWithLogWrapper


class ParentExampleModelWrapper(ModelWrapper):

    model_name = 'edc_example.parentexample'
    next_url_attrs = {'edc_example.parentexample': ['f1']}
    extra_querystring_attrs = {'edc_example.parentexample': ['f2', 'f3']}
    url_instance_attrs = ['f1', 'f2', 'f3']  # only expose these instance attrs for url options
    url_namespace = 'edc-example'


class ExampleModelWrapper(ModelWrapper):

    model_name = 'edc_example.example'
    next_url_attrs = {'edc_example.example': ['f1']}
    extra_querystring_attrs = {'edc_example.example': ['f2', 'f3']}
    url_instance_attrs = ['f1', 'f2', 'f3']  # only expose these instance attrs for url options
    url_namespace = 'edc-example'


class ExampleLogEntryModelWrapper(ModelWrapper):

    model_name = 'edc_example.examplelogentry'
    next_url_attrs = {'edc_example.examplelogentry': ['example_identifier', 'example_log']}
    extra_querystring_attrs = {'edc_example.examplelogentry': ['f2', 'f3']}
    url_instance_attrs = ['example_identifier', 'example_log']  # only expose these instance attrs for url options
    url_namespace = 'edc-example'

    @property
    def example_identifier(self):
        return self._original_object.example_log.example.example_identifier

    @property
    def survey(self):
        return 'survey_one'


class ExampleModelWithLogWrapper(ModelWithLogWrapper):

    model_wrapper_class = ExampleModelWrapper
    log_entry_model_wrapper_class = ExampleLogEntryModelWrapper


class ParentExampleModelWithLogWrapper(ModelWithLogWrapper):

    model_wrapper_class = ParentExampleModelWrapper
    log_entry_model_wrapper_class = ExampleLogEntryModelWrapper

    parent_model_wrapper_class = ExampleModelWrapper
    parent_lookup = 'example'


@tag('me2')
class TestModelWrapper(TestCase):

    def setUp(self):
        self.example = Example.objects.create(f1=5, f2=6)
        self.wrapped_object = ExampleModelWrapper(self.example)

    def test_model_wrapper_sets_original_object_attr(self):
        self.assertEqual(self.wrapped_object.example, self.example)

    def test_model_wrapper_urls(self):
        self.assertEqual(
            self.wrapped_object.add_url_name, 'edc-example:admin:edc_example_example_add')
        self.assertEqual(
            self.wrapped_object.change_url_name, 'edc-example:admin:edc_example_example_change')

    def test_model_wrapper_extra_querystring(self):
        self.assertIn(
            'f2={}'.format(self.example.f2),
            self.wrapped_object.extra_querystring)
        self.assertIn(
            'f3={}'.format(self.example.f3),
            self.wrapped_object.extra_querystring)

    def test_model_wrapper_next_url(self):
        self.assertEqual(
            self.wrapped_object.next_url, 'listboard_url,f1&f1=5')


@tag('me1')
class TestModelWithLogWrapper(TestCase):

    def setUp(self):
        self.example = Example.objects.create(
            example_identifier='123456-0', f1=5, f2=6)
        self.parent_example = ParentExample.objects.create(example=self.example)
        self.example_log = ExampleLog.objects.create(example=self.example)
        ExampleLogEntry.objects.create(example_log=self.example_log)
        ExampleLogEntry.objects.create(example_log=self.example_log)
        ExampleLogEntry.objects.create(example_log=self.example_log)
        self.example = Example.objects.get(id=self.example.id)
        self.wrapped_object = ExampleModelWithLogWrapper(self.example)

    def test_object_without_log(self):
        self.example.examplelog.delete()
        self.example = Example.objects.get(id=self.example.id)
        self.wrapped_object = ExampleModelWithLogWrapper(self.example)
        self.assertIsNotNone(self.wrapped_object.log_entry_model)
        self.assertIsNotNone(self.wrapped_object.log_model)
        self.assertIsNotNone(self.wrapped_object.log_model_names)

    def test_object_with_log_only(self):
        self.example.examplelog.examplelogentry_set.all().delete()
        self.example = Example.objects.get(id=self.example.id)
        self.wrapped_object = ExampleModelWithLogWrapper(self.example)
        self.assertIsNotNone(self.wrapped_object.log_entry_model)
        self.assertIsNotNone(self.wrapped_object.log_model)
        self.assertIsNotNone(self.wrapped_object.log_model_names)
        self.assertIsNotNone(self.wrapped_object.log)
        self.assertIsNotNone(self.wrapped_object.log_entry)
        self.assertTrue(self.wrapped_object.log_entry._mocked_object)

    def test_object_with_log_entry(self):
        self.assertIsNotNone(self.wrapped_object.log_entry_model)
        self.assertIsNotNone(self.wrapped_object.log_model)
        self.assertIsNotNone(self.wrapped_object.log_model_names)
        self.assertIsNotNone(self.wrapped_object.log)
        self.assertIsNotNone(self.wrapped_object.log_entry)
        self.assertTrue(self.wrapped_object.log_entry._mocked_object)

    def test_object_with_current_log_entry(self):
        self.wrapped_object = ExampleModelWithLogWrapper(
            self.example, report_datetime=get_utcnow())
        self.assertIsNotNone(self.wrapped_object.log_entry_model)
        self.assertIsNotNone(self.wrapped_object.log_model)
        self.assertIsNotNone(self.wrapped_object.log_model_names)
        self.assertIsNotNone(self.wrapped_object.log)
        self.assertIsNotNone(self.wrapped_object.log_entry)
        try:
            self.wrapped_object.log_entry._mocked_object
            self.fail('Unexpected got a mocked log entry object')
        except AttributeError:
            pass

        self.assertIn(
            'example_log={}'.format(self.example.examplelog.id),
            self.wrapped_object.log_entry.next_url)

        self.assertIn(
            'listboard_url',
            self.wrapped_object.log_entry.next_url.split('&')[0])

        self.assertIn(
            'example_log',
            self.wrapped_object.log_entry.next_url.split('&')[0])

        self.assertIn(
            'example_identifier',
            self.wrapped_object.log_entry.next_url.split('&')[0])

        self.assertIn(
            'example_identifier={}'.format(self.example.example_identifier),
            self.wrapped_object.log_entry.next_url)

    def test_object_with_different_parent_and_model(self):
        self.wrapped_object = ParentExampleModelWithLogWrapper(
            self.parent_example, report_datetime=get_utcnow())
        self.assertIsNotNone(self.wrapped_object.log_entry_model)
        self.assertIsNotNone(self.wrapped_object.log_model)
        self.assertIsNotNone(self.wrapped_object.log_model_names)
        self.assertIsNotNone(self.wrapped_object.log)
        self.assertIsNotNone(self.wrapped_object.log_entry)
        self.assertIsNotNone(self.wrapped_object.parent)
        self.assertEqual(self.wrapped_object.parent.id, str(self.parent_example.example.id))
        try:
            self.wrapped_object.log_entry._mocked_object
            self.fail('Unexpected got a mocked log entry object')
        except AttributeError:
            pass

        self.assertIn(
            'example_log={}'.format(self.example.examplelog.id),
            self.wrapped_object.log_entry.next_url)

        self.assertIn(
            'listboard_url',
            self.wrapped_object.log_entry.next_url.split('&')[0])

        self.assertIn(
            'example_log',
            self.wrapped_object.log_entry.next_url.split('&')[0])

        self.assertIn(
            'example_identifier',
            self.wrapped_object.log_entry.next_url.split('&')[0])

        self.assertIn(
            'example_identifier={}'.format(self.example.example_identifier),
            self.wrapped_object.log_entry.next_url)
