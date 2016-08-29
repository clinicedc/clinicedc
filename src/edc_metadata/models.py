from django.apps import apps as django_apps
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from edc_visit_tracking.model_mixins import VisitModelMixin
from edc_base.model.models import BaseUuidModel

from .model_mixins import CrfMetadataModelMixin, RequisitionMetadataModelMixin


class CrfMetadata(CrfMetadataModelMixin, BaseUuidModel):

    class Meta(CrfMetadataModelMixin.Meta):
        app_label = 'edc_metadata'


class RequisitionMetadata(RequisitionMetadataModelMixin, BaseUuidModel):

    class Meta(RequisitionMetadataModelMixin.Meta):
        app_label = 'edc_metadata'


@receiver(post_save, weak=False, dispatch_uid="metadata_on_post_save")
def metadata_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw:
        if isinstance(instance, VisitModelMixin):
            pass
            # These are visit models
#             crf_metadata_helper = CrfMetadataHelper(instance.appointment, visit_instance=instance)
#             crf_metadata_helper.add_or_update_for_visit()
#             requisition_metadata_helper = RequisitionMetadataHelper(instance.appointment, instance)
#             requisition_metadata_helper.add_or_update_for_visit()
#             # update rule groups through the rule group controller, instance is a visit_instance
#             RegisteredSubject = django_apps.get_app_config('edc_registration').model
#             site_rule_groups.update_rules_for_source_model(RegisteredSubject, instance)
#             site_rule_groups.update_rules_for_source_fk_model(RegisteredSubject, instance)
#
#             instance = instance.custom_post_update_crf_metadata()  # see CrfMetadataMixin for visit model
#
#             if instance.survival_status == DEAD:
#                 instance.require_death_report()
#             else:
#                 instance.undo_require_death_report()
#             if instance.study_status == OFF_STUDY:
#                 instance.require_off_study_report()
#             else:
#                 instance.undo_require_off_study_report()
#         else:
#             try:
#                 change_type = 'I' if created else 'U'
#                 sender.entry_metadata_manager.instance = instance
#                 sender.entry_metadata_manager.visit_instance = getattr(
#                     instance, sender.entry_metadata_manager.visit_attr_name)
#                 try:
#                     sender.entry_metadata_manager.target_requisition_panel = getattr(instance, 'panel')
#                 except AttributeError as e:
#                     if 'target_requisition_panel' in str(e):
#                         pass
#                 sender.entry_metadata_manager.update_metadata(change_type)
#                 if sender.entry_metadata_manager.instance:
#                     sender.entry_metadata_manager.run_rule_groups()
#             except AttributeError as e:
#                 if 'entry_metadata_manager' in str(e):
#                     pass


@receiver(pre_delete, weak=False, dispatch_uid="metadata_on_pre_delete")
def metadata_on_pre_delete(sender, instance, using, **kwargs):
    """Delete metadata if the visit tracking instance is deleted."""
    if isinstance(instance, VisitModelMixin):
        app_config = django_apps.get_app_config('edc_metadata')
        app_config.crf_metadata
        app_config.crf_metadata.objects.filter(appointment=instance.appointment).delete()
        app_config.requisition_metadata.objects.filter(appointment=instance.appointment).delete()
    else:
        try:
            sender.entry_metadata_manager.instance = instance
            sender.entry_metadata_manager.visit_instance = getattr(
                instance, sender.entry_metadata_manager.visit_attr_name)
            try:
                sender.entry_metadata_manager.target_requisition_panel = getattr(instance, 'panel')
            except AttributeError as e:
                pass
            sender.entry_metadata_manager.update_metadata('D')
        except AttributeError as e:
            if 'entry_metadata_manager' in str(e):
                pass
            else:
                raise
