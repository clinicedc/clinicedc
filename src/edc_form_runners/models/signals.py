from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_crf.model_mixins import CrfModelMixin, CrfNoManagerModelMixin
from edc_lab.model_mixins import RequisitionModelMixin
from edc_model.models import BaseUuidModel

from ..exceptions import FormRunnerModelAdminNotFound, FormRunnerModelFormNotFound
from ..get_form_runner_by_src_id import get_form_runner_by_src_id
from ..utils import get_edc_form_runners_enabled


@receiver(
    post_save,
    weak=False,
    dispatch_uid="update_issue_on_post_save",
)
def update_issue_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Updates Issue data on post-save"""
    if not raw and not update_fields:
        if get_edc_form_runners_enabled():
            if isinstance(
                instance, (CrfModelMixin, CrfNoManagerModelMixin, RequisitionModelMixin)
            ) and isinstance(instance, (BaseUuidModel,)):
                try:
                    runner = get_form_runner_by_src_id(
                        src_id=instance.id,
                        model_name=sender._meta.label_lower,
                    )
                except (FormRunnerModelAdminNotFound, FormRunnerModelFormNotFound):
                    pass
                else:
                    runner.run_one()
