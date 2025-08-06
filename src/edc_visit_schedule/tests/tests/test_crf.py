from django.test import TestCase

from edc_visit_schedule.visit import Crf
from edc_visit_schedule.visit.crf import CrfModelNotProxyModelError


class TestCrfCollection(TestCase):
    def test_crf_ok(self):
        try:
            Crf(show_order=1, model="visit_schedule_app.CrfOne")
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

        try:
            Crf(show_order=1, model="visit_schedule_app.CrfOneProxyOne")
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

        try:
            Crf(show_order=1, model="visit_schedule_app.CrfTwo")
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

        try:
            Crf(show_order=1, model="visit_schedule_app.CrfThree")
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_proxy_child_crf_with_allow_proxy_parent_clash_ok(self):
        try:
            Crf(
                show_order=1,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            )
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_proxy_root_crf_with_allow_proxy_parent_clash_raises(self):
        with self.assertRaises(CrfModelNotProxyModelError) as cm:
            Crf(show_order=1, model="visit_schedule_app.CrfOne", shares_proxy_root=True)
        self.assertIn(
            "Invalid use of `shares_proxy_root=True`. CRF model is not a proxy model.",
            str(cm.exception),
        )
        self.assertIn("visit_schedule_app.crfone", str(cm.exception))

    def test_non_proxy_crf_with_allow_proxy_parent_clash_raises(self):
        with self.assertRaises(CrfModelNotProxyModelError) as cm:
            Crf(
                show_order=1,
                model="visit_schedule_app.CrfThree",
                shares_proxy_root=True,
            )
        self.assertIn(
            "Invalid use of `shares_proxy_root=True`. CRF model is not a proxy model.",
            str(cm.exception),
        )
        self.assertIn("visit_schedule_app.crfthree", str(cm.exception))
