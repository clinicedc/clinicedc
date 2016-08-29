from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.db.utils import IntegrityError

from edc_constants.constants import REQUIRED, KEYED, NO, NOT_REQUIRED, UNKEYED
from edc_content_type_map.models import ContentTypeMap

from .choices import ENTRY_STATUS
from .models import CrfEntry, LabEntry, RequisitionPanel


class MetaDataModelMixin(models.Model):

    """ Base model for list of required entries by registered_subject. """

    current_entry_title = models.CharField(
        max_length=250,
        null=True)

    entry_status = models.CharField(
        max_length=25,
        choices=ENTRY_STATUS,
        default=UNKEYED,
        db_index=True)

    due_datetime = models.DateTimeField(
        null=True,
        blank=True)

    report_datetime = models.DateTimeField(
        null=True,
        blank=True)

    entry_comment = models.TextField(
        max_length=250,
        null=True,
        blank=True)

    close_datetime = models.DateTimeField(
        null=True,
        blank=True)

    fill_datetime = models.DateTimeField(
        null=True,
        blank=True)

    def is_required(self):
        return self.entry_status != NOT_REQUIRED

    def is_not_required(self):
        return not self.is_required()

    def include_for_dispatch(self):
        return True

    class Meta:
        abstract = True


class CrfMetaDataModelMixin(MetaDataModelMixin):

    """Class to manipulate meta data after entry_meta_data_manager for CRFs and requisitions."""

    crf_entry = models.ForeignKey(CrfEntry)

    def natural_key(self):
        return self.appointment.natural_key() + self.crf_entry.natural_key()

    @property
    def crf_meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').crf_meta_data_model

    @property
    def requisition_meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').requisition_meta_data_model

    def custom_post_update_crf_meta_data(self):
        return self

    def crf_is_required(self, appointment, app_label, model_name, create=None):
        """Sets the CRF status to REQUIRED."""
        return self.change_crf_status(
            REQUIRED, appointment, app_label, model_name, create)

    def crf_is_not_required(self, appointment, app_label, model_name, delete=None):
        """Sets the CRF status to NOT REQUIRED."""
        crf_meta_data = None
        if delete:
            try:
                obj = self.crf_meta_data_model.objects.get(
                    crf_entry__app_label=app_label,
                    crf_entry__model_name=model_name,
                    appointment=self.get_base_appointment(appointment),
                    entry_status__in=[REQUIRED, NOT_REQUIRED])
                obj.delete()
            except self.crf_meta_data_model.DoesNotExist:
                pass
        else:
            crf_meta_data = self.change_crf_status(
                NOT_REQUIRED, appointment, app_label, model_name)
        return crf_meta_data

    def requisition_is_required(self, appointment, app_label, model_name, panel_name, create=None):
        """Sets the Requisition status to REQUIRED."""
        self.change_requisition_status(
            REQUIRED, appointment, app_label, model_name, panel_name, create)

    def requisition_is_not_required(self, appointment, app_label, model_name, panel_name, delete=None):
        """Sets the Requisition status to NOT REQUIRED."""
        self.change_requisition_status(
            NOT_REQUIRED, appointment, app_label, model_name, panel_name)
        if delete:
            self.requisition_meta_data_model.objects.filter(
                lab_entry__app_label=app_label,
                lab_entry__model_name=model_name,
                appointment=self.get_base_appointment(appointment),
                lab_entry__requisition_panel__name=panel_name,
                entry_status__in=[REQUIRED, NOT_REQUIRED])

    def require_off_study_report(self):
        """Changes the meta data so that only the off study form is required.

        * if the off study form does not exist it will be created.
        * if a form is already KEYED it will not be changed.
        * if visit.require_crfs, then only the off study meta data is changed.
        """
        app_label = self.off_study_model._meta.app_label
        model_name = self.off_study_model._meta.model_name
        content_type_map = ContentTypeMap.objects.get(app_label=app_label, module_name=model_name)
        with transaction.atomic():
            try:
                CrfEntry.objects.create(
                    content_type_map=content_type_map,
                    visit_definition=self.appointment.visit_definition,
                    entry_order=0,
                    app_label=app_label,
                    model_name=model_name,
                    default_entry_status=REQUIRED,
                    additional=True)
            except IntegrityError:
                pass
        if self.require_crfs == NO:
            self.change_all_to_not_required()
        self.crf_is_required(
            self.appointment, app_label, model_name, create=True)

    def require_death_report(self):
        """Changes the meta data so that only the death and
        off study forms are required, unless require_crfs is True."""
        app_label = self.death_report_model._meta.app_label
        model_name = self.death_report_model._meta.model_name
        content_type_map = ContentTypeMap.objects.get(app_label=app_label, module_name=model_name)
        with transaction.atomic():
            try:
                CrfEntry.objects.create(
                    content_type_map=content_type_map,
                    visit_definition=self.appointment.visit_definition,
                    entry_order=0,
                    app_label=app_label,
                    model_name=model_name,
                    default_entry_status=REQUIRED,
                    additional=True)
            except IntegrityError:
                pass
        self.crf_is_required(
            self.appointment, app_label, model_name, create=True)

    def undo_require_off_study_report(self):
        """Revert off study CRF to not required.

        off_study_model attr is always set.
        """
        off_study_app_label = self.off_study_model._meta.app_label
        off_study_model_name = self.off_study_model._meta.model_name
        self.crf_is_not_required(
            self.appointment, off_study_app_label, off_study_model_name, delete=True)

    def undo_require_death_report(self):
        """Revert death report CRF to not required.

        death_report_model attr is NOT always set."""
        if self.death_report_model:
            app_label = self.death_report_model._meta.app_label
            death_model_name = self.death_report_model._meta.model_name
            self.crf_is_not_required(self.appointment, app_label, death_model_name, delete=True)

    def change_to_unscheduled_visit(self, appointment):
        """Changes all meta data to not required."""
        self.change_all_to_not_required()

    def change_all_to_not_required(self):
        """Changes all meta data to not required."""
        with transaction.atomic():
            base_appointment = self.get_base_appointment(self.appointment)
            self.crf_meta_data_model.objects.filter(
                appointment=base_appointment,
                registered_subject=self.appointment.registered_subject).exclude(
                    entry_status__in=[NOT_REQUIRED, KEYED]).exclude(
                        crf_entry__model_name=self.death_report_model._meta.model_name).update(
                    entry_status=NOT_REQUIRED)
            self.requisition_meta_data_model.objects.filter(
                appointment=base_appointment,
                registered_subject=self.appointment.registered_subject).exclude(
                    entry_status__in=[NOT_REQUIRED, KEYED]).update(
                    entry_status=NOT_REQUIRED)

    def change_crf_status(self, entry_status, appointment, app_label, model_name, create=None):
        """Toggles a CRF's entry status between REQUIRED / NOT REQUIRED."""
        crf_meta_data = None
        if entry_status in [REQUIRED, NOT_REQUIRED]:
            with transaction.atomic():
                try:
                    crf_meta_data = self.crf_meta_data_model.objects.get(
                        crf_entry__app_label=app_label,
                        crf_entry__model_name=model_name,
                        appointment=self.get_base_appointment(appointment),
                        entry_status__in=[x for x in [REQUIRED, NOT_REQUIRED] if x != entry_status])
                    crf_meta_data.entry_status = entry_status
                    crf_meta_data.save()
                except self.crf_meta_data_model.DoesNotExist:
                    if create:
                        crf_meta_data = self.create_crf_meta_data(
                            appointment, app_label, model_name, entry_status)
        return crf_meta_data

    def change_requisition_status(
            self, entry_status, appointment, app_label, model_name, panel_name, create=None):
        """Toggles a Requisition's entry status between REQUIRED / NOT REQUIRED."""
        if entry_status in [REQUIRED, NOT_REQUIRED]:
            try:
                requisition_meta_data = self.requisition_meta_data_model.objects.get(
                    lab_entry__app_label=app_label,
                    lab_entry__model_name=model_name,
                    appointment=self.get_base_appointment(appointment),
                    lab_entry__requisition_panel__name=panel_name,
                    entry_status__in=[x for x in [REQUIRED, NOT_REQUIRED] if x != entry_status])
                requisition_meta_data.entry_status = entry_status
                requisition_meta_data.save()
            except self.requisition_meta_data_model.DoesNotExist:
                if create:
                    requisition_meta_data = self.create_requisition_meta_data(
                        appointment, app_label, model_name, panel_name,
                        entry_status)

    def create_crf_meta_data(self, appointment, app_label, model_name, entry_status):
        """Creates or updates existing CRF meta data to given entry_status."""
        crf_entry = None
        base_appointment = self.get_base_appointment(appointment)
        try:
            crf_entry = CrfEntry.objects.get(
                app_label=app_label,
                model_name=model_name,
                visit_definition=base_appointment.visit_definition)
        except CrfEntry.DoesNotExist:
            raise ImproperlyConfigured('Crf Entry does not exist. Check AppConfiguration. Got {}.{}.'.format(
                app_label, model_name))
        try:
            crf_meta_data = self.crf_meta_data_model.objects.create(
                crf_entry=crf_entry,
                appointment=base_appointment,
                registered_subject=base_appointment.registered_subject,
                entry_status=entry_status)
        except IntegrityError:
            crf_meta_data = None
        return crf_meta_data

    def create_requisition_meta_data(self, appointment, app_label, model_name, panel_name, entry_status):
        """Creates or updates existing requisition meta data to given entry_status."""
        lab_entry = None
        base_appointment = self.get_base_appointment(appointment)
        requisition_panel = RequisitionPanel.objects.get(panel_name=panel_name)
        try:
            lab_entry = LabEntry.objects.get(
                model_name=model_name,
                requisition_panel=requisition_panel,
                visit_definition=base_appointment.visit_definition)
        except LabEntry.DoesNotExist:
            raise ImproperlyConfigured('Lab Entry does not exist. Check AppConfiguration. Got {}.{} panel {}.'.format(
                app_label, model_name, requisition_panel.name))
        try:
            requisition_meta_data = self.requisition_meta_data_model.objects.create(
                lab_entry=lab_entry,
                appointment=base_appointment,
                lab_entry__requisition_panel=requisition_panel,
                entry_status=entry_status)
        except IntegrityError:
            requisition_meta_data = None
        return requisition_meta_data

    def get_base_appointment(self, appointment):
        """Returns the base appointment (CODE.0).

        More than one appointments may span for a given visit code.
        The appointments are incremented using a decimal, e.g. 1000.0,
        1000.1, 1000.2 , etc. 1000.0 is the "base" appointment."""
        if appointment.visit_instance != '0':
            appointment = appointment.__class__.objects.get(
                registered_subject=appointment.registered_subject,
                visit_instance='0', visit_definition=appointment.visit_definition)
        return appointment

    class Meta:
        abstract = True
        verbose_name = "Crf Metadata"
        verbose_name_plural = "Crf Metadata"
        ordering = ['registered_subject', 'crf_entry', 'appointment']
        unique_together = ['registered_subject', 'crf_entry', 'appointment']


class RequisitionMetaDataModelMixin(MetaDataModelMixin):

    """Subject-specific list of required and scheduled lab as per normal visit schedule."""

    lab_entry = models.ForeignKey(LabEntry)

    def __str__(self):
        return '{}: {}' % (self.registered_subject.subject_identifier, self.lab_entry.requisition_panel.name)

    def natural_key(self):
        return self.appointment.natural_key() + self.lab_entry.natural_key()

    class Meta:
        abstract = True
        verbose_name = "Requisition Meta Data"
        verbose_name_plural = "Requisition Meta Data"
        ordering = ['registered_subject', 'lab_entry__requisition_panel__name', 'appointment', ]
        unique_together = ['registered_subject', 'lab_entry', 'appointment', ]
