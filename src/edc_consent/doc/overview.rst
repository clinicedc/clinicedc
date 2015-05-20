
Overview
========

:mod:`bhp_consent` handles consent issues as they relate to data entry. In a nutshell:

    * a subject must be consented before data is collected.
    * For protocols with more than one version of a consent, models and model fields may be restricted depending on the
      subject's consent 
    * a consent covers a fixed time period before which data entry may not begin and after which data entry stops.
    
The class :class:`ConsentHelper` provides the methods to enforce consent versions and time periods. It is accessed
both from a model's :func:`save` method when subclassed from the class :class:`base_consented_uuid_model.BaseConsentedUuidModel` 
and a modelform's :func:`clean` method when the subclassed from class :class:`base_consented_model_form.BaseConsentedModelForm`.

Protocol subject consents are subclasses from :class:`BaseConsent` where each subject has a unique entry.

:mod:`bhp_consent` provides a model :class:ConsentCatalogue` with one entry per consent type. Attached to each consent 
type are all the model names that are covered by that consent type. These model names are listed in the model :class:`AttahcedModel`.

Using a consent from another subject
++++++++++++++++++++++++++++++++++++

For some protocols, the consent of one subject covers the data collection for the other. For example, a mother's
consent covers data collection for the infant. In such a case, models for the subject that does not consent (infant) must return the 
subject identifier of the consenting subject (mother). The :class:consent_helper.ConsentHelper` class will check for the method 
:func:`get_consenting_subject_identifier`::

    def get_consenting_subject_identifier(self):
        """Returns mother's identifier."""
        return self.infant_visit.appointment.registered_subject.relative_identifier
        
or::

    def get_consenting_subject_identifier(self):
        """Returns mother's identifier."""
        return self.registered_subject.relative_identifier


