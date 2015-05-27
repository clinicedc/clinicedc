from lis.core.lab_grading.classes import GradeFlag


class ClinicGradeFlag(GradeFlag):

    def __init__(self, reference_list, result_item, **kwargs):
        """Extracts parameters from lab_clinic_api.ResultItem, which has a different structure to that in lab_result_item.ResultItem."""
        test_code = result_item.test_code
        gender = result_item.result.order.aliquot.receive.registered_subject.gender
        dob = result_item.result.order.aliquot.receive.registered_subject.dob
        drawn_datetime = result_item.result.order.aliquot.receive.receive_datetime
        release_datetime = result_item.result_item_datetime
        subject_identifier = result_item.result.order.aliquot.receive.registered_subject.subject_identifier
        subject_type = result_item.get_subject_type()
        super(ClinicGradeFlag, self).__init__(
            subject_identifier,
            subject_type,
            reference_list,
            test_code,
            gender,
            dob,
            drawn_datetime,
            release_datetime,
            **kwargs)

    def get_lab_tracker_group_name(self):
        """Returns a group name to use when filtering on values in the lab_tracker class.

        See :mod:edc.subject.lab_tracker"""
        return 'HIV'
