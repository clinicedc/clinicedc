class RsDialect:
    def __init__(self, obj=None):
        self.obj = obj

    @property
    def select_registered_subject(self):
        """Returns an SQL statement that joins visit, appt, and registered_subject."""
        sql = (  # nosec B608
            "SELECT R.subject_identifier, R.screening_identifier, R.dob, "  # nosec B608
            "R.gender, R.subject_type, R.sid, "  # nosec B608
            "R.screening_age_in_years, R.registration_status, "  # nosec B608
            "R.registration_datetime, "  # nosec B608
            "R.randomization_datetime "  # nosec B608
            f"FROM {self.obj.registered_subject_tbl} as R "  # nosec B608
        )
        return sql, None
