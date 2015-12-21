Scheduling Appointments
=======================

Appointments are created according to the visit definition by default in the :func:`save` method 
in models based on :class:`BaseRegisteredSubjectModel` in module :mod:`bhp_registration`.

For example::

    AppointmentHelper().create_all(self.registered_subject, self.__class__.__name__.lower())