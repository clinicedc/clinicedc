from django.test import TestCase, tag

from ..site import site_dataframe_handlers
from ..df_handlers import DfHandler
from ..site import SiteDataframeHandlerNotFound, AlreadyRegistered


class TestSiteHandlers(TestCase):

    def setUp(self):
        site_dataframe_handlers.registry = {}
        site_dataframe_handlers.loaded = False

    def test_register_as_class(self):
        site_dataframe_handlers.register(handler_cls=DfHandler)
        self.assertIn(DfHandler.__name__, site_dataframe_handlers.registry)
        self.assertRaises(
            AlreadyRegistered,
            site_dataframe_handlers.register, handler_cls=DfHandler)

    def test_register_by_app_label_reference(self):
        app_label = 'my_app_label'
        site_dataframe_handlers.register(
            handler_cls=DfHandler, app_labels=[app_label])
        self.assertEqual(DfHandler, site_dataframe_handlers.get_for(app_label))
        self.assertRaises(
            SiteDataframeHandlerNotFound,
            site_dataframe_handlers.get_for, 'blah')

    def test_register_by_model_reference(self):
        model = 'my_app_label.somemodel'
        site_dataframe_handlers.register(
            handler_cls=DfHandler, models=[model])
        self.assertEqual(DfHandler, site_dataframe_handlers.get_for(model))
