

class CrfDialect:

    def __init__(self, obj=None):
        self.obj = obj

    @property
    def select_visit_and_related(self):
        """Returns an SQL statement that joins visit, appt, and registered_subject.
        """
        sql = (
            'SELECT R.subject_identifier, R.screening_identifier, R.dob, '
            'R.gender, R.subject_type, R.sid, '
            'V.report_datetime as visit_datetime, A.appt_status, '
            'A.visit_code, A.timepoint, V.reason, '
            'A.appt_datetime, A.timepoint_datetime,  '
            'R.screening_age_in_years, R.registration_status, R.registration_datetime, '
            'R.randomization_datetime, V.survival_status, V.last_alive_date, '
            f'V.id as {self.obj.visit_column} '
            f'from {self.obj.appointment_tbl} as A '
            f'LEFT JOIN {self.obj.visit_tbl} as V on A.id=V.appointment_id '
            f'LEFT JOIN {self.obj.registered_subject_tbl} as R '
            'on A.subject_identifier=R.subject_identifier '
        )
        return sql, None

    @property
    def select_visit_and_related2(self):
        """Returns an SQL statement that joins visit, appt, and registered_subject.

        This is for older EDC versions that use this schema.
        """
        sql = (
            'SELECT R.subject_identifier, R.screening_identifier, R.dob, '
            'R.gender, R.subject_type, R.sid, '
            'V.report_datetime as visit_datetime, A.appt_status, V.study_status, '
            'VDEF.code as visit_code, VDEF.title as visit_title, VDEF.time_point, V.reason, '
            'A.appt_datetime, A.timepoint_datetime, A.best_appt_datetime, '
            'R.screening_age_in_years, R.registration_status, R.registration_datetime, '
            'R.randomization_datetime, V.survival_status, V.last_alive_date, '
            f'V.id as {self.obj.visit_column} '
            f'from {self.obj.appointment_tbl} as  A '
            f'LEFT JOIN {self.obj.visit_tbl} as V on A.id=V.appointment_id '
            f'LEFT JOIN {self.obj.visit_definition_tbl} as VDEF '
            'on A.visit_definition_id=VDEF.id '
            f'LEFT JOIN {self.obj.registered_subject_tbl} as R '
            'on A.registered_subject_id=R.id '
        )
        return sql, None

    @property
    def select_inline_visit_and_related(self):
        sql = (
            'SELECT R.subject_identifier, R.screening_identifier, R.dob, '
            'R.gender, R.subject_type, R.sid, '
            'V.report_datetime as visit_datetime, A.appt_status, V.study_status, '
            'VDEF.code as visit_code, VDEF.title as visit_title, VDEF.time_point, V.reason, '
            'A.appt_datetime, A.timepoint_datetime, A.best_appt_datetime, '
            'R.screening_age_in_years, R.registration_status, R.registration_datetime, '
            'R.randomization_datetime, V.survival_status, V.last_alive_date, '
            f'V.id as {self.obj.visit_column} '
            f'from {self.obj.appointment_tbl} as A '
            f'LEFT JOIN {self.obj.visit_tbl} as V on A.id=V.appointment_id '
            f'LEFT JOIN {self.obj.visit_definition_tbl} as VDEF '
            'on A.visit_definition_id=VDEF.id '
            f'LEFT JOIN {self.obj.registered_subject_tbl} as R '
            'on A.registered_subject_id=R.id '
        )
        return sql, None
