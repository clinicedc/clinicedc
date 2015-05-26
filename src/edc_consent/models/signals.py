from django.apps import apps
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from edc_registration.models import RegisteredSubject
from edc_content_type_map.models import ContentTypeMap

from .consent_catalogue import ConsentCatalogue
from .base_consent import BaseConsent
from .base_consented_uuid_model import BaseConsentedUuidModel
from .attached_model import AttachedModel


@receiver(post_save, weak=False, dispatch_uid='update_or_create_registered_subject_on_post_save')
def update_or_create_registered_subject_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates or creates an instance of RegisteredSubject on the sender instance.

    Sender instance is a Consent"""
    if not raw:
        if isinstance(instance, (BaseConsent, )):
            try:
                # if instance.registered_subject:
                # has attr and is set to an instance of registered subject -- update
                for field_name, value in instance.registered_subject_options.iteritems():
                    setattr(instance.registered_subject, field_name, value)
                # RULE: subject identifier is ONLY allocated by a edc_consent:
                instance.registered_subject.subject_identifier = instance.subject_identifier
                instance.registered_subject.save(using=using)
            except AttributeError:
                # this should not be used
                # self does not have a foreign key to RegisteredSubject but RegisteredSubject
                # still needs to be created or updated
                try:
                    registered_subject = RegisteredSubject.objects.using(using).get(
                        subject_identifier=instance.subject_identifier)
                    for field_name, value in instance.registered_subject_options.iteritems():
                        setattr(registered_subject, field_name, value)
                    if created:
                        registered_subject.subject_identifier = instance.subject_identifier
                    registered_subject.save(using=using)
                except RegisteredSubject.DoesNotExist:
                    RegisteredSubject.objects.using(using).create(
                        subject_identifier=instance.subject_identifier,
                        **instance.registered_subject_options)


@receiver(pre_save, weak=False, dispatch_uid='is_consented_instance_on_pre_save')
def is_consented_instance_on_pre_save(sender, instance, raw, **kwargs):
    if not raw:
        if isinstance(instance, BaseConsentedUuidModel):
            if instance.get_requires_consent():
                if not instance.is_consented_for_instance():
                    raise TypeError(
                        'Data may not be collected. Model {0} is not '
                        'covered by a valid edc_consent for this subject.'
                        .format(instance._meta.object_name))
                instance.validate_versioned_fields()


@receiver(post_save, weak=False, dispatch_uid='add_models_to_catalogue')
def add_models_to_catalogue(sender, instance, raw, **kwargs):
    """Automatically adds all models to the AttachedModel model if
    ConsentCatalogue.add_for_app is a valid app_label."""
    if not raw:
        if sender == ConsentCatalogue and instance.add_for_app:
            try:
                app = apps.get_app(instance.add_for_app)
                models = apps.get_models(app)
                for model in models:
                    if ('edc_consent' not in model._meta.object_name.lower() and
                            'audit' not in model._meta.object_name.lower()):
                        try:
                            content_type_map = ContentTypeMap.objects.get(model=model._meta.object_name.lower())
                            AttachedModel.objects.get(
                                consent_catalogue=instance, content_type_map=content_type_map)
                        except AttachedModel.DoesNotExist:
                                AttachedModel.objects.create(
                                    consent_catalogue=instance, content_type_map=content_type_map)
                        except ContentTypeMap.DoesNotExist as err_message:
                            raise ContentTypeMap.DoesNotExist(
                                'ContentTypeMap for model {} not found (table {}). Referenced in the edc_consent '
                                'catalogue {} but does not exist. {}'.format(
                                    model._meta.object_name.lower(), model._meta.db_table, instance, err_message))
            except AttributeError:
                pass


@receiver(post_save, weak=False, dispatch_uid='update_consent_history')
def update_consent_history(sender, instance, raw, created, using, **kwargs):
    """Updates the edc_consent history model with this instance if such model exists."""
    if not raw:
        if isinstance(instance, BaseConsent):
            instance.update_consent_history(created, using)


@receiver(post_delete, weak=False, dispatch_uid='delete_consent_history')
def delete_consent_history(sender, instance, using, **kwargs):
    """Updates the edc_consent history model with this instance if such model exists."""
    if isinstance(instance, BaseConsent):
        instance.delete_consent_history(instance._meta.app_label, instance._meta.object_name, instance.pk, using)
