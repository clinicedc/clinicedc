from django.contrib import admin


class ModelAdminLocatorMixin:
    def __init__(self, *args):
        self.get_radio_fields()
        super().__init__(*args)

    def get_fields(self, request, obj=None):
        return self.get_fields(self, request, obj=obj) + [
            "mail_address",
            "home_visit_permission",
            "physical_address",
            "may_follow_up",
            "subject_cell",
            "subject_cell_alt",
            "subject_phone",
            "subject_phone_alt",
            "may_call_work",
            "subject_work_place",
            "subject_work_phone",
            "may_contact_someone",
            "contact_name",
            "contact_rel",
            "contact_physical_address",
            "contact_cell",
            "contact_phone",
        ]

    def get_radio_fields(self):
        self.radio_fields.update(
            {
                "home_visit_permission": admin.VERTICAL,
                "may_follow_up": admin.VERTICAL,
                "may_call_work": admin.VERTICAL,
                "may_contact_someone": admin.VERTICAL,
            }
        )
