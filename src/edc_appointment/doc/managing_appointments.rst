Managing Appointments
=====================


Scheduling Appointments
+++++++++++++++++++++++

Appointments are created according to the visit definition defined in :mod:`bhp_visit` model :class:`visit_definition`. 
Default code does this in the :func:`save` method in models that inherit from 
:class:`BaseRegisteredSubjectModel` in module :mod:`bhp_registration`.

For example::

    AppointmentHelper().create_all(self.registered_subject, self.__class__.__name__.lower())
    
    
Confirming appointments
+++++++++++++++++++++++

The :class:`pre_appointment_contact_log` can be used to track effort to contact subjects, modify the 
scheduled date, change the type (e.g., clinic, telephone, home) and confirm an appointment.

    