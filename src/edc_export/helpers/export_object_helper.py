from .export_helper import ExportHelper

from ..classes import ExportObjectAsCsv


class ExportObjectHelper(ExportHelper):

    """
    For example:
        from edc.export.helpers import ExportObjectHelper
        from edc.export.classes import ExportPlan
        from apps.bcpp_export.helpers import Member

        dct = {
            'name': 'test_plan',
            'fields': [],
            'extra_fields': {},
            'exclude': [],
            'header': True,
            'track_history': True,
            'show_all_fields': True,
            'delimiter': '|',
            'encrypt': False,
            'strip': True,
            'target_path': '~/export_to_cdc',
            'notification_plan_name': 'referral_file_to_cdc',
        }

        export_plan = ExportPlan(**dct)
        members = []
        for household_member in HouseholdMember.objects.filter(
                household_structure__household__plot__community='sefophe')[0:150]:
            member = Member(household_member)
            member.customize_for_csv()
            members.append(member)
        if not export_plan.fields:
            export_plan.fields = members[0].data.keys()
        export_object_helper = ExportObjectHelper(members, export_plan)
    """

    def __init__(self, export_plan, filename=None, fields=None, delimiter=None, exception_cls=None, notify=None):
        if not export_plan.fields:
            export_plan.fields = fields
        if not export_plan.delimiter:
            export_plan.delimiter = delimiter
        super(ExportObjectHelper, self).__init__(export_plan, exception_cls=exception_cls, notify=notify)
        self.export_filename = filename
        self.writer_cls = ExportObjectAsCsv

    def reset(self):
        """Resets instance attr."""
        self.transactions = []
        self.export_datetime = None
        self.export_filename = None
        self.exit_status = None

    @property
    def writer(self):
        """Returns an instance of ExportJsonAsCsv for the list of transactions to export."""
        return self.writer_cls(
            self.export_filename,
            fields=self.export_plan.fields,
            exclude=self.export_plan.exclude,
            extra_fields=self.export_plan.extra_fields,
            header=self.export_plan.header,
            track_history=self.export_plan.track_history,
            show_all_fields=self.export_plan.show_all_fields,
            delimiter=self.export_plan.delimiter,
            encrypt=self.export_plan.encrypt,
            strip=self.export_plan.strip,
            target_path=self.export_plan.target_path,
            notification_plan_name=self.export_plan.notification_plan_name,
            export_datetime=self.export_datetime)
