from edc_pharma.print_profile import site_profiles

from django.test import TestCase, tag


@tag("DispenseProfile")
class TestDispenseProfile(TestCase):
    def test_site_profiles(self):
        self.assertTrue(site_profiles)

    def test_site_profiles_single_dose(self):
        single_dose_profile = site_profiles.get("enrollment.single_dose")
        self.assertTrue(single_dose_profile)
        self.assertTrue(len(single_dose_profile.medication_types), 3)

    def test_site_profiles_single_dose1(self):
        single_dose_profile = site_profiles.get("enrollment.single_dose")
        self.assertEqual(
            single_dose_profile.medication_types.get("liposomal_amphotericin").name,
            "liposomal_amphotericin",
        )
        self.assertEqual(
            single_dose_profile.medication_types.get("fluconazole_1200mg").name,
            "fluconazole_1200mg",
        )
        self.assertEqual(
            single_dose_profile.medication_types.get("flucytosine").name, "flucytosine"
        )
        self.assertEqual(len(single_dose_profile.medication_types), 3)

    def test_site_profiles_single_dose2(self):
        single_dose_profile = site_profiles.get("followup.single_dose")
        self.assertEqual(len(single_dose_profile.medication_types), 1)
        self.assertEqual(
            single_dose_profile.medication_types.get("fluconazole_800mg").name,
            "fluconazole_800mg",
        )
        self.assertEqual(len(single_dose_profile.medication_types), 1)

    def test_site_profiles_control_arm(self):
        control_arm = site_profiles.get("enrollment.control")
        self.assertTrue(len(control_arm.medication_types), 2)
        self.assertEqual(
            control_arm.medication_types.get("amphotericin").name, "amphotericin"
        )
        self.assertEqual(
            control_arm.medication_types.get("flucytosine").name, "flucytosine"
        )

    def test_site_profiles_control_arm_followup(self):
        control_arm = site_profiles.get("followup.control")
        self.assertEqual(
            control_arm.medication_types.get("fluconazole_800mg").name,
            "fluconazole_800mg",
        )
        self.assertEqual(len(control_arm.medication_types), 1)
