from django.test import TestCase, tag
from django.urls import reverse


class TestUrls(TestCase):
    def test_requisition_listboard_url(self):
        url = reverse("requisition_listboard_url")
        self.assertEqual("/listboard/requisition/", url)

        url = reverse("requisition_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/requisition/1/", url)

    def test_receive_listboard_url(self):
        url = reverse("receive_listboard_url")
        self.assertEqual("/listboard/receive/", url)

        url = reverse("receive_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/receive/1/", url)

    def test_process_listboard_url(self):
        url = reverse("process_listboard_url")
        self.assertEqual("/listboard/process/", url)

        url = reverse("process_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/process/1/", url)

    def test_pack_listboard_url(self):
        url = reverse("pack_listboard_url")
        self.assertEqual("/listboard/pack/", url)

        url = reverse("pack_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/pack/1/", url)

    def test_aliquot_listboard_url(self):
        url = reverse("aliquot_listboard_url")
        self.assertEqual("/listboard/aliquot/", url)

        url = reverse("aliquot_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/aliquot/1/", url)

    def test_manifest_listboard_url(self):
        url = reverse("manifest_listboard_url")
        self.assertEqual("/listboard/manifest/", url)

        url = reverse("manifest_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/manifest/1/", url)

    def test_result_listboard_url(self):
        url = reverse("result_listboard_url")
        self.assertEqual("/listboard/result/", url)

        url = reverse("result_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/listboard/result/1/", url)

    def test_manage_box_listboard_url(self):
        url = reverse("manage_box_listboard_url", kwargs=dict(action_name="manage"))
        self.assertEqual("/listboard/box/manage/", url)

        url = reverse(
            "manage_box_listboard_url",
            kwargs=dict(action_name="manage", box_identifier="ABC123"),
        )
        self.assertEqual("/listboard/box/manage/ABC123/", url)

        url = reverse(
            "manage_box_listboard_url",
            kwargs=dict(action_name="manage", box_identifier="ABC123", page=1),
        )
        self.assertEqual("/listboard/box/manage/ABC123/1/", url)

    def test_verify_box_listboard_url(self):
        url = reverse(
            "verify_box_listboard_url", kwargs=dict(action_name="verify", position=22)
        )
        self.assertEqual("/listboard/box/verify/22/", url)

        url = reverse(
            "verify_box_listboard_url",
            kwargs=dict(action_name="verify", box_identifier="ABC123", position=22),
        )
        self.assertEqual("/listboard/box/verify/ABC123/22/", url)

        url = reverse(
            "verify_box_listboard_url",
            kwargs=dict(
                action_name="verify", box_identifier="ABC123", position=22, page=1
            ),
        )
        self.assertEqual("/listboard/box/verify/ABC123/22/1/", url)

    def test_manage_manifest_listboard_url(self):
        url = reverse(
            "manage_manifest_listboard_url",
            kwargs=dict(action_name="manage", manifest_identifier="ABC123", page=1),
        )
        self.assertEqual("/listboard/manifest/manage/ABC123/1/", url)

        url = reverse(
            "manage_manifest_listboard_url",
            kwargs=dict(action_name="manage", manifest_identifier="ABC123"),
        )
        self.assertEqual("/listboard/manifest/manage/ABC123/", url)

        url = reverse(
            "manage_manifest_listboard_url", kwargs=dict(action_name="manage")
        )
        self.assertEqual("/listboard/manifest/manage/", url)

    def test_manage_box_item_form_action_url(self):
        url = reverse(
            "manage_box_item_form_action_url",
            kwargs=dict(action_name="manage", box_identifier="ABC123"),
        )
        self.assertEqual("/box/ABC123/manage/", url)

    def test_verify_box_item_form_action_url(self):
        url = reverse(
            "verify_box_item_form_action_url",
            kwargs=dict(action_name="verify", box_identifier="ABC123", position=22),
        )
        self.assertEqual("/box/ABC123/verify/22/", url)

    def test_manage_manifest_item_form_action_url(self):
        url = reverse(
            "manage_manifest_item_form_action_url",
            kwargs=dict(action_name="manage", manifest_identifier="ABC123"),
        )
        self.assertEqual("/manifest/ABC123/manage/", url)

    def test_requisition_form_action_url(self):
        url = reverse("requisition_form_action_url")
        self.assertEqual("/requisition/", url)

    def test_receive_form_action_url(self):
        url = reverse("receive_form_action_url")
        self.assertEqual("/requisition/receive/", url)

    def test_process_url(self):
        url = reverse("process_form_action_url")
        self.assertEqual("/requisition/process/", url)

    def test_pack_form_action_url(self):
        url = reverse("pack_form_action_url")
        self.assertEqual("/requisition/pack/", url)

    def test_manifest_url(self):
        url = reverse("manifest_form_action_url")
        self.assertEqual("/manifest/", url)

    def test_aliquot_form_action_url(self):
        url = reverse("aliquot_form_action_url")
        self.assertEqual("/aliquot/", url)

    def test_home_url(self):
        url = reverse("home_url")
        self.assertEqual("/", url)
