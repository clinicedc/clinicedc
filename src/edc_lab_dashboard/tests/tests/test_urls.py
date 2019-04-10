from django.test import TestCase, tag
from django.urls import reverse


class TestUrls(TestCase):
    def test_requisition_listboard_url(self):
        url = reverse("edc_lab_dashboard:requisition_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/requisition/", url)

        url = reverse(
            "edc_lab_dashboard:requisition_listboard_url", kwargs=dict(page=1)
        )
        self.assertEqual("/edc_lab_dashboard/listboard/requisition/1/", url)

    def test_receive_listboard_url(self):
        url = reverse("edc_lab_dashboard:receive_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/receive/", url)

        url = reverse("edc_lab_dashboard:receive_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/edc_lab_dashboard/listboard/receive/1/", url)

    def test_process_listboard_url(self):
        url = reverse("edc_lab_dashboard:process_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/process/", url)

        url = reverse("edc_lab_dashboard:process_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/edc_lab_dashboard/listboard/process/1/", url)

    def test_pack_listboard_url(self):
        url = reverse("edc_lab_dashboard:pack_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/pack/", url)

        url = reverse("edc_lab_dashboard:pack_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/edc_lab_dashboard/listboard/pack/1/", url)

    def test_aliquot_listboard_url(self):
        url = reverse("edc_lab_dashboard:aliquot_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/aliquot/", url)

        url = reverse("edc_lab_dashboard:aliquot_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/edc_lab_dashboard/listboard/aliquot/1/", url)

    def test_manifest_listboard_url(self):
        url = reverse("edc_lab_dashboard:manifest_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/manifest/", url)

        url = reverse("edc_lab_dashboard:manifest_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/edc_lab_dashboard/listboard/manifest/1/", url)

    def test_result_listboard_url(self):
        url = reverse("edc_lab_dashboard:result_listboard_url")
        self.assertEqual("/edc_lab_dashboard/listboard/result/", url)

        url = reverse("edc_lab_dashboard:result_listboard_url", kwargs=dict(page=1))
        self.assertEqual("/edc_lab_dashboard/listboard/result/1/", url)

    def test_manage_box_listboard_url(self):
        url = reverse(
            "edc_lab_dashboard:manage_box_listboard_url",
            kwargs=dict(action_name="manage"),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/box/manage/", url)

        url = reverse(
            "edc_lab_dashboard:manage_box_listboard_url",
            kwargs=dict(action_name="manage", box_identifier="ABC123"),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/box/manage/ABC123/", url)

        url = reverse(
            "edc_lab_dashboard:manage_box_listboard_url",
            kwargs=dict(action_name="manage", box_identifier="ABC123", page=1),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/box/manage/ABC123/1/", url)

    def test_verify_box_listboard_url(self):
        url = reverse(
            "edc_lab_dashboard:verify_box_listboard_url",
            kwargs=dict(action_name="verify", position=22),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/box/verify/22/", url)

        url = reverse(
            "edc_lab_dashboard:verify_box_listboard_url",
            kwargs=dict(action_name="verify", box_identifier="ABC123", position=22),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/box/verify/ABC123/22/", url)

        url = reverse(
            "edc_lab_dashboard:verify_box_listboard_url",
            kwargs=dict(
                action_name="verify", box_identifier="ABC123", position=22, page=1
            ),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/box/verify/ABC123/22/1/", url)

    def test_manage_manifest_listboard_url(self):
        url = reverse(
            "edc_lab_dashboard:manage_manifest_listboard_url",
            kwargs=dict(action_name="manage", manifest_identifier="ABC123", page=1),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/manifest/manage/ABC123/1/", url)

        url = reverse(
            "edc_lab_dashboard:manage_manifest_listboard_url",
            kwargs=dict(action_name="manage", manifest_identifier="ABC123"),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/manifest/manage/ABC123/", url)

        url = reverse(
            "edc_lab_dashboard:manage_manifest_listboard_url",
            kwargs=dict(action_name="manage"),
        )
        self.assertEqual("/edc_lab_dashboard/listboard/manifest/manage/", url)

    def test_manage_box_item_form_action_url(self):
        url = reverse(
            "edc_lab_dashboard:manage_box_item_form_action_url",
            kwargs=dict(action_name="manage", box_identifier="ABC123"),
        )
        self.assertEqual("/edc_lab_dashboard/box/ABC123/manage/", url)

    def test_verify_box_item_form_action_url(self):
        url = reverse(
            "edc_lab_dashboard:verify_box_item_form_action_url",
            kwargs=dict(action_name="verify", box_identifier="ABC123", position=22),
        )
        self.assertEqual("/edc_lab_dashboard/box/ABC123/verify/22/", url)

    def test_manage_manifest_item_form_action_url(self):
        url = reverse(
            "edc_lab_dashboard:manage_manifest_item_form_action_url",
            kwargs=dict(action_name="manage", manifest_identifier="ABC123"),
        )
        self.assertEqual("/edc_lab_dashboard/manifest/ABC123/manage/", url)

    def test_requisition_form_action_url(self):
        url = reverse("edc_lab_dashboard:requisition_form_action_url")
        self.assertEqual("/edc_lab_dashboard/requisition/", url)

    def test_receive_form_action_url(self):
        url = reverse("edc_lab_dashboard:receive_form_action_url")
        self.assertEqual("/edc_lab_dashboard/requisition/receive/", url)

    def test_process_url(self):
        url = reverse("edc_lab_dashboard:process_form_action_url")
        self.assertEqual("/edc_lab_dashboard/requisition/process/", url)

    def test_pack_form_action_url(self):
        url = reverse("edc_lab_dashboard:pack_form_action_url")
        self.assertEqual("/edc_lab_dashboard/requisition/pack/", url)

    def test_manifest_url(self):
        url = reverse("edc_lab_dashboard:manifest_form_action_url")
        self.assertEqual("/edc_lab_dashboard/manifest/", url)

    def test_aliquot_form_action_url(self):
        url = reverse("edc_lab_dashboard:aliquot_form_action_url")
        self.assertEqual("/edc_lab_dashboard/aliquot/", url)

    def test_home_url(self):
        url = reverse("edc_lab_dashboard:home_url")
        self.assertEqual("/edc_lab_dashboard/", url)
