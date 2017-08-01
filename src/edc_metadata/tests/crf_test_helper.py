from model_mommy import mommy

from ..models import CrfMetadata, RequisitionMetadata
from ..constants import REQUIRED, NOT_REQUIRED


class CrfTestHelper:

    """A test class to help create CRFs and manipulate
    metadata.
    """

    def mommy_options(self, report_datetime):
        """Override the default recipe options for your
        'mommy recipe {label_lower: {key: value}, ...}.
        """
        return {}

    def crf_metadata_obj(self, model, entry_status, visit_code):
        return CrfMetadata.objects.filter(
            entry_status=entry_status,
            model=model,
            visit_code=visit_code,
            subject_identifier=self.subject_identifier)

    def requisition_metadata_obj(
            self, model, entry_status, visit_code, panel_name):
        return RequisitionMetadata.objects.filter(
            entry_status=entry_status,
            model=model,
            subject_identifier=self.subject_identifier,
            panel_name=panel_name,
            visit_code=visit_code)

    def get_crfs(self, visit_code=None, subject_identifier=None):
        """Return a queryset of crf metadata for the visit.
        """
        return CrfMetadata.objects.filter(
            subject_identifier=subject_identifier,
            visit_code=visit_code).order_by('show_order')

    def get_crfs_by_entry_status(self, visit_code=None, entry_status=None,
                                 subject_identifier=None):
        """Return a queryset of crf metadata for the visit by entry_status.
        """
        return self.get_crfs(
            visit_code=visit_code, subject_identifier=subject_identifier).filter(
                entry_status__in=entry_status).order_by('show_order')

    def complete_crfs(self, visit_code=None, visit=None, visit_attr=None,
                      entry_status=None, subject_identifier=None):
        """Complete all CRFs in a visit by looping through metadata.

        Revisit the metadata on each loop as rule_groups may change
        the entry status of CRFs.
        """
        entry_status = entry_status or [REQUIRED, NOT_REQUIRED]
        visit_attr = visit_attr or 'subject_visit'
        if not isinstance(entry_status, (list, tuple)):
            entry_status = [entry_status]
        completed_crfs = []
        while True:
            for crf in self.get_crfs_by_entry_status(
                    visit_code=visit_code,
                    entry_status=entry_status,
                    subject_identifier=subject_identifier):
                options = self.mommy_options(
                    visit.report_datetime).get(crf.model, {})
                options.update({
                    visit_attr: visit,
                    'report_datetime': visit.report_datetime})
                completed_crfs.append(
                    mommy.make_recipe(crf.model, **options))
            if not self.get_crfs_by_entry_status(
                    visit_code=visit_code, entry_status=entry_status,
                    subject_identifier=subject_identifier):
                break
        return completed_crfs

    def complete_required_crfs(self, visit_code=None, visit=None,
                               visit_attr=None, subject_identifier=None):
        return self.complete_crfs(
            visit_code=visit_code,
            visit=visit,
            visit_attr=visit_attr,
            entry_status=REQUIRED,
            subject_identifier=subject_identifier)
