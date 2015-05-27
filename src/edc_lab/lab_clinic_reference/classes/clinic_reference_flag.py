from lis.core.lab_reference.classes import ReferenceFlag


class ClinicReferenceFlag(ReferenceFlag):

    def __init__(self, reference_list, result_item, **kwargs):
        test_code = result_item.test_code
        gender = result_item.result.order.aliquot.receive.registered_subject.gender
        dob = result_item.result.order.aliquot.receive.registered_subject.dob
        drawn_datetime = result_item.result.order.aliquot.receive.receive_datetime
        release_datetime = result_item.result_item_datetime
        subject_identifier = result_item.result.order.aliquot.receive.registered_subject.subject_identifier
        subject_type = result_item.get_subject_type()
        super(ClinicReferenceFlag, self).__init__(
            subject_identifier,
            subject_type,
            reference_list,
            test_code,
            gender,
            dob,
            drawn_datetime,
            release_datetime,
            **kwargs)
