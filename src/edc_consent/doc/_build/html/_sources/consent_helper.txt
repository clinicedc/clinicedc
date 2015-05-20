
ConsentHelper Class
===================

The :class:`consent_helper.ConsentHelper` class provides methods to help manage subject consents and the data models covered by consent.

It may be subclassed at the protocol module to override :func:`clean_versioned_field` to add more detailed
data checks for versioned fields than the default. For example, from mpepu_maternal.classes::

    from edc.subject.consent.classes import ConsentHelper
    
    class MaternalEligibilityConsentHelper(ConsentHelper):
        def clean_versioned_field(self, field_value, field, start_datetime, consent_version):
            if getattr(self.get_subject_instance(), 'feeding_choice') == 'Yes':
                if field.name == 'maternal_haart' and getattr(self.get_subject_instance(), 'is_cd4_low'):
                    if  field_value == 'No' and getattr(self.get_subject_instance(), 'is_cd4_low') < 250:
                        raise self.get_exception_cls()('Mother must be willing to '
                                                       'initiate HAART if feeding choice is BF and '
                                                       'CD4 < 250 for data captured during or after '
                                                       'version {2}. [{3}]'.format(field.name, 
                                                                                   start_datetime, 
                                                                                   consent_version, 
                                                                                   field.verbose_name[0:50]))
                                                       

The new class will be acccessed in the ModelForm :func:`clean` so that the above checks are applied to the versioned fields.