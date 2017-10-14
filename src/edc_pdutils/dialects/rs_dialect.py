

class RsDialect:

    def __init__(self, obj=None):
        self.obj = obj

    @property
    def select_registered_subject(self):
        """Returns an SQL statement that joins visit, appt, and registered_subject.
        """
        sql = (
            'SELECT R.subject_identifier, R.screening_identifier, R.dob, '
            'R.gender, R.subject_type, R.sid, '
            'R.screening_age_in_years, R.registration_status, R.registration_datetime, '
            'R.randomization_datetime '
            f'FROM {self.obj.registered_subject_tbl} as R '
        )
        return sql, None
