from edc_pharma.medications import medications

from ..print_profile import DispenseProfile


class SiteDispenseProfiles:

    """Registers all defined dispense profile for profiles.
    """

    def __init__(self):
        self._registry = {}

    def __repr__(self):
        return f'{self.__class__.__name__}(loaded={self.loaded})'

    def get(self, name=None):
        """ Returns a dispense profile for given dispense profile name.
        """
        return self._registry.get(name)

    def register(self, dispense_profile=None):
        """Registers a dispense profile instance using the dispense profile name
        as the key.
        """
        if dispense_profile:
            profile_type = dispense_profile.profile_type
            self._registry.update({
                f'{dispense_profile.name}.{profile_type}': dispense_profile})

    @property
    def profiles(self):
        """Returns all registered dispense profiles.
        """
        return self._registry


site_profiles = SiteDispenseProfiles()

single_dose_enrollment = DispenseProfile(
    name='enrollment', profile_type='single_dose')
single_dose_enrollment.add_medication_type(
    medications.get('liposomal_amphotericin'))
single_dose_enrollment.add_medication_type(
    medications.get('fluconazole_1200mg'))
single_dose_enrollment.add_medication_type(medications.get('flucytosine'))
site_profiles.register(single_dose_enrollment)

single_dose_followup = DispenseProfile(
    name='followup', profile_type='single_dose')
single_dose_followup.add_medication_type(medications.get('fluconazole_800mg'))
site_profiles.register(single_dose_followup)

control_arm_enrollemnt = DispenseProfile(
    name='enrollment', profile_type='control')
control_arm_enrollemnt.add_medication_type(medications.get('amphotericin'))
control_arm_enrollemnt.add_medication_type(medications.get('flucytosine'))
site_profiles.register(control_arm_enrollemnt)

control_followup_profile = DispenseProfile(
    name='followup', profile_type='control')
control_followup_profile.add_medication_type(
    medications.get('fluconazole_800mg'))
site_profiles.register(control_followup_profile)
