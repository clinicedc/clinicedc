from django.apps import apps as django_apps
from django.test import TestCase, tag
from django.db.models.signals import post_save

from ..data_fixers import fix_null_related_action_items, fix_null_action_item_fk
from ..models import ActionItem
from ..signals import update_or_create_action_item_on_post_save
from .action_items import register_actions
from .models import FormOne, FormTwo
from .models import SubjectIdentifierModel


class TestUtils(TestCase):
    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = "edc_action_item.subjectidentifiermodel"
        self.subject_identifier = "12345"
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier
        )

    def test_fix_null_related_action_items(self):

        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        form_two.refresh_from_db()

        self.assertEqual(form_one.action_item, form_two.related_action_item)

        # break it ....
        # set related_action_item to None
        form_two.related_action_item = None
        form_two.save_base()
        form_two.refresh_from_db()
        form_two.action_item.related_action_item = None
        form_two.action_item.save_base()
        form_two.action_item.refresh_from_db()

        # it's broken ...
        # assert related_action_items are None
        self.assertIsNone(form_two.related_action_item)
        self.assertIsNone(form_two.action_item.related_action_item)

        # fix
        fix_null_related_action_items(django_apps)

        # assert related_action_item are no longer None
        form_two.refresh_from_db()
        form_two.action_item.refresh_from_db()

        self.assertEqual(form_one.action_item, form_two.action_item.related_action_item)

    def test_fix_null_related_action_items2(self):

        fix_null_related_action_items(django_apps)

        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        form_two_a = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        form_two_b = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )

        self.assertEqual(form_one.action_item, form_two_b.related_action_item)

        # set related_action_item to None
        form_two_b.related_action_item = None
        form_two_b.action_item.related_action_item = None
        post_save.disconnect(dispatch_uid="update_or_create_action_item_on_post_save")
        form_two_b.action_item.save()
        form_two_b.save_base()
        post_save.connect(
            update_or_create_action_item_on_post_save,
            dispatch_uid="update_or_create_action_item_on_post_save",
        )

        form_two_b.refresh_from_db()
        form_two_b.action_item.refresh_from_db()

        # assert related_action_items are None
        self.assertIsNone(form_two_b.related_action_item)
        self.assertIsNone(form_two_b.action_item.related_action_item)

        # fix
        fix_null_related_action_items(django_apps)

        # assert related_action_item are NOT None
        form_two_b.refresh_from_db()
        self.assertEqual(
            form_one.action_item, form_two_b.action_item.related_action_item
        )
        self.assertEqual(form_one.action_item, form_two_b.related_action_item)
        self.assertEqual(form_two_a.action_item, form_two_b.parent_action_item)

    def test_fix_null_related_action_items3(self):

        # fix_null_related_action_items(django_apps)

        # form_one -> form_two_a -> form_two_b

        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        form_two_a = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        form_two_b = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )

        # set related_action_item to None
        form_two_a.parent_action_item = form_one.action_item
        form_two_a.action_item.parent_action_item = form_one.action_item

        form_two_a.action_item.related_action_item = None
        form_two_a.related_action_item = None
        form_two_a.action_item.save_base()

        post_save.disconnect(dispatch_uid="update_or_create_action_item_on_post_save")
        form_two_a.save_base()
        form_two_a.refresh_from_db()

        form_two_b.related_action_item = None
        form_two_b.action_item.related_action_item = None
        form_two_b.action_item.save_base()
        form_two_b.save_base()
        form_two_b.refresh_from_db()

        # set parent b to wrong parent
        form_two_b.parent_action_item = form_one.action_item
        form_two_b.action_item.parent_action_item = form_one.action_item
        form_two_b.action_item.save_base()
        form_two_b.save_base()
        form_two_b.refresh_from_db()
        post_save.connect(
            update_or_create_action_item_on_post_save,
            dispatch_uid="update_or_create_action_item_on_post_save",
        )

        self.assertEqual(form_one.action_item, form_two_b.parent_action_item)
        self.assertEqual(
            form_one.action_item, form_two_b.action_item.parent_action_item
        )

        # fix
        fix_null_related_action_items(django_apps)

        form_two_a.refresh_from_db()
        form_two_a.action_item.refresh_from_db()
        form_two_a.parent_action_item.refresh_from_db()
        form_two_b.refresh_from_db()
        form_two_b.action_item.refresh_from_db()
        form_two_b.parent_action_item.refresh_from_db()

        # assert related_action_item are NOT None
        self.assertEqual(
            form_one.action_item, form_two_a.action_item.related_action_item
        )
        self.assertEqual(form_one.action_item, form_two_b.related_action_item)

        self.assertEqual(form_two_a.parent_action_item, form_two_a.related_action_item)

        self.assertEqual(form_one.action_item, form_two_a.parent_action_item)

        self.assertEqual(
            form_one.action_item, form_two_a.action_item.parent_action_item
        )

        # assert parent was fixed
        self.assertEqual(
            form_two_a.action_item, form_two_b.action_item.parent_action_item
        )
        self.assertEqual(form_two_a.action_item, form_two_b.parent_action_item)

        self.assertNotEqual(
            form_two_b.parent_action_item, form_two_b.related_action_item
        )

    def test_fix_null_action_item_fk(self):
        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        fix_null_action_item_fk(
            django_apps, app_label="edc_action_item", models=["formone", "formtwo"]
        )
