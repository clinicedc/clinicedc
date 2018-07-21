from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@receiver(post_save, weak=False, dispatch_uid='offstudy_model_on_post_save')
def offstudy_model_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        try:
            sender.offstudy_cls
        except AttributeError:
            pass
        else:
            if not created:
                visit_schedule = site_visit_schedules.get_visit_schedule(
                    visit_schedule_name=instance.visit_schedule_name)
                schedule = visit_schedule.schedules.get(instance.schedule_name)
                schedule.refresh_enrolled_schedule(
                    subject_identifier=instance.subject_identifier,
                    consent_identifier=instance.consent_identifier)
