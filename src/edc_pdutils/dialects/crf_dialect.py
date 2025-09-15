class CrfDialect:
    def __init__(self, obj=None):
        self.obj = obj

    @property
    def select_visit_and_related(self):
        """Returns an SQL statement that joins visit, appt, and registered_subject."""
        sql = (
            "SELECT R.subject_identifier, R.screening_identifier, R.dob, "  # nosec
            "R.gender, R.subject_type, R.sid, "  # nosec
            "V.report_datetime as visit_datetime, A.appt_status, "  # nosec
            "A.visit_code, A.timepoint, V.reason, "  # nosec
            "A.appt_datetime, A.timepoint_datetime,  "  # nosec
            "R.screening_age_in_years, R.registration_status, "  # nosec
            "R.registration_datetime, "  # nosec
            "R.randomization_datetime, V.survival_status, V.last_alive_date, "  # nosec
            f"V.id as {self.obj.visit_column} "  # nosec
            f"from {self.obj.appointment_tbl} as A "  # nosec
            f"LEFT JOIN {self.obj.visit_tbl} as V on A.id=V.appointment_id "  # nosec
            f"LEFT JOIN {self.obj.registered_subject_tbl} as R "  # nosec
            "on A.subject_identifier=R.subject_identifier "  # nosec
        )
        return sql, None

    @property
    def select_visit_and_related2(self):
        """Returns an SQL statement that joins visit, appt, and registered_subject.

        This is for older EDC versions that use this schema.
        """
        # nosec
        sql = (
            "SELECT R.subject_identifier, R.screening_identifier, R.dob, "  # nosec
            "R.gender, R.subject_type, R.sid, "  # nosec
            "V.report_datetime as visit_datetime, A.appt_status, V.study_status, "  # nosec
            "VDEF.code as visit_code, VDEF.title as visit_title, VDEF.time_point, "  # nosec
            "V.reason, "  # nosec
            "A.appt_datetime, A.timepoint_datetime, A.best_appt_datetime, "  # nosec
            "R.screening_age_in_years, R.registration_status, "  # nosec
            "R.registration_datetime, "  # nosec
            "R.randomization_datetime, V.survival_status, V.last_alive_date, "  # nosec
            f"V.id as {self.obj.visit_column} "  # nosec
            f"from {self.obj.appointment_tbl} as  A "  # nosec
            f"LEFT JOIN {self.obj.visit_tbl} as V on A.id=V.appointment_id "  # nosec
            f"LEFT JOIN {self.obj.visit_definition_tbl} as VDEF "  # nosec
            "on A.visit_definition_id=VDEF.id "  # nosec
            f"LEFT JOIN {self.obj.registered_subject_tbl} as R "  # nosec
            "on A.registered_subject_id=R.id "  # nosec
        )
        return sql, None

    @property
    def select_inline_visit_and_related(self):
        # nosec
        sql = (
            "SELECT R.subject_identifier, R.screening_identifier, R.dob, "  # nosec
            "R.gender, R.subject_type, R.sid, "  # nosec
            "V.report_datetime as visit_datetime, A.appt_status, V.study_status, "  # nosec
            "VDEF.code as visit_code, VDEF.title as visit_title, VDEF.time_point, "  # nosec
            "V.reason, "  # nosec
            "A.appt_datetime, A.timepoint_datetime, A.best_appt_datetime, "  # nosec
            "R.screening_age_in_years, R.registration_status, "  # nosec
            "R.registration_datetime, "  # nosec
            "R.randomization_datetime, V.survival_status, V.last_alive_date, "  # nosec
            f"V.id as {self.obj.visit_column} "  # nosec
            f"from {self.obj.appointment_tbl} as A "  # nosec
            f"LEFT JOIN {self.obj.visit_tbl} as V on A.id=V.appointment_id "  # nosec
            f"LEFT JOIN {self.obj.visit_definition_tbl} as VDEF "  # nosec
            "on A.visit_definition_id=VDEF.id "  # nosec
            f"LEFT JOIN {self.obj.registered_subject_tbl} as R "  # nosec
            "on A.registered_subject_id=R.id "  # nosec
        )
        return sql, None
