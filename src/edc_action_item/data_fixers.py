import re
import sys

from django.core.exceptions import (
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from django.db import connection
from django.db.models.signals import post_delete, post_save, pre_save
from edc_constants.constants import CLOSED, NEW, OPEN

from .site_action_items import site_action_items


def fix_null_historical_action_identifier(app_label, models):
    """Fix null action_identifiers from previous versions."""
    with connection.cursor() as cursor:
        for model in models:
            tbl = f"{app_label}_historical{model}"
            if not re.match("([a-z]+)_historical_([a-z]+)", tbl):
                raise ValueError("Invalid table name when building sql statement")
            tbl = re.match("([a-z]+)_historical_([a-z]+)", tbl).group()
            sql = (
                f"update {tbl} set action_identifier=id "  # nosec B608
                "where action_identifier is null"  # nosec B608
            )
            cursor.execute(sql)


def fix_null_action_item_fk(apps, app_label, models):
    """Re-save instances to update action_item FKs."""
    action_item_cls = apps.get_model("edc_action_item", "ActionItem")
    post_save.disconnect(dispatch_uid="serialize_on_save")
    pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")

    fix_null_action_items(apps)

    for model in models:
        model_cls = apps.get_model(app_label, model)
        model_cls.action_name = [
            action.name
            for action in site_action_items.registry.values()
            if action.get_reference_model()
            and action.get_reference_model().split(".")[1].lower() == model.lower()
        ][0]
        if model_cls.action_name:
            for obj in model_cls.objects.all():
                sys.stdout.write(f"fixing {model_cls.action_name} action_item for {obj}.\n")
                if not obj.action_item:
                    try:
                        obj.action_item_id = action_item_cls.objects.get(
                            action_identifier=obj.action_identifier
                        ).pk
                    except MultipleObjectsReturned as e:
                        qs = action_item_cls.objects.filter(
                            action_identifier=obj.action_identifier
                        ).order_by("created")
                        raise MultipleObjectsReturned(f"{e} {qs}.")
                    else:
                        obj.save_base(update_fields=["action_item_id"])
                else:
                    try:
                        obj.save()
                    except MultipleObjectsReturned:
                        sys.stdout.write(f"Failed to resave {repr(obj)}")


def fix_null_action_items(apps):
    action_item_cls = apps.get_model("edc_action_item", "ActionItem")
    try:
        action_items = action_item_cls.objects.filter(
            parent_action_identifier__isnull=False, parent_action_item__isnull=True
        )
    except FieldError as e:
        print(e)
    else:
        for action_item in action_items:
            if not action_item.parent_action_item and action_item.parent_action_identifier:
                parent_action_item = action_item_cls.objects.get(
                    action_identifier=action_item.parent_action_identifier
                )
                updated = (
                    action_item_cls.objects.filter(
                        parent_action_identifier=action_item.parent_action_identifier,
                        parent_action_item__isnull=True,
                        linked_to_reference=True,
                    )
                    .exclude(action_identifier=action_item.related_action_identifier)
                    .update(parent_action_item=parent_action_item)
                )
                sys.stdout.write(
                    f" setting parent_action_items for {parent_action_item}. Got {updated}\n"
                )
    try:
        action_items = action_item_cls.objects.filter(
            related_action_identifier__isnull=False, related_action_item__isnull=True
        )
    except FieldError as e:
        print(e)
    else:
        for action_item in action_items:
            if not action_item.related_action_item and action_item.related_action_identifier:
                related_action_item = action_item_cls.objects.get(
                    action_identifier=action_item.related_action_identifier
                )
                updated = (
                    action_item_cls.objects.filter(
                        related_action_identifier=action_item.related_action_identifier,
                        related_action_item__isnull=True,
                    )
                    .exclude(action_identifier=action_item.related_action_identifier)
                    .update(related_action_item=related_action_item)
                )
                sys.stdout.write(
                    f" setting related_action_items for "
                    f"{related_action_item}. Got {updated}\n"
                )


def fix_null_related_action_items(apps):  # noqa
    """"""
    post_save.disconnect(dispatch_uid="serialize_on_save")
    pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")
    action_item_cls = apps.get_model("edc_action_item", "ActionItem")

    fix_null_action_items(apps)

    related_action_items = {}
    for action_cls in site_action_items.registry.values():
        if action_cls.related_reference_fk_attr:
            for action_item in action_item_cls.objects.filter(
                related_action_item__isnull=True, action_type__name=action_cls.name
            ):
                related_action_item = None
                reference_obj = None
                try:
                    reference_obj = action_item.reference_obj
                except ObjectDoesNotExist:
                    print("No reference object", action_item)
                else:
                    try:
                        related_reference_obj = getattr(
                            reference_obj, action_cls.related_reference_fk_attr
                        )
                    except ObjectDoesNotExist:
                        print("related_reference_obj does not exist")
                        if action_item.parent_action_item:
                            related_action_item = action_item.parent_action_item
                        elif reference_obj.parent_action_item:
                            related_action_item = reference_obj.parent_action_item
                    else:
                        related_action_item = related_reference_obj.action_item
                if related_action_item:
                    related_action_items.update({related_action_item: related_action_item})
                    action_item.related_action_item = related_action_item
                    action_item.save()
                    if reference_obj:
                        reference_obj.related_action_item = related_action_item  # noqa
                        reference_obj.save()
            if (
                action_item_cls.objects.filter(
                    related_action_item__isnull=True, action_type__name=action_cls.name
                ).count()
                > 0
            ):
                print("Some related action identifiers are still `none`")

    # verify sequence
    for related_action_item in related_action_items:
        fix_action_item_sequence(
            action_item_cls,
            action_identifier=related_action_item.action_identifier,
            subject_identifier=related_action_item.subject_identifier,
        )


def fix_action_item_sequence(action_item_cls, action_identifier=None, subject_identifier=None):
    """Verify the parent sequence of action items given the
    related action item.
    """
    parent_action_item = action_item_cls.objects.get(
        subject_identifier=subject_identifier, action_identifier=action_identifier
    )
    last_action_item = None
    for action_item in action_item_cls.objects.filter(
        related_action_item=parent_action_item
    ).order_by("created"):
        action_item.parent_action_item = last_action_item or parent_action_item
        action_item.save()
        action_item.refresh_from_db()
        if action_item.status in [CLOSED, OPEN]:
            action_item.reference_obj.parent_action_item = parent_action_item
            action_item.reference_obj.save()
            action_item.reference_obj.refresh_from_db()
        last_action_item = action_item


def fix_duplicate_singleton_action_items(apps, name=None):
    post_delete.disconnect(dispatch_uid="serialize_on_post_delete")
    post_save.disconnect(dispatch_uid="serialize_on_save")
    pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")

    registered_subject_cls = apps.get_model("edc_registration", "RegisteredSubject")
    action_item_cls = apps.get_model("edc_action_item", "ActionItem")

    action_cls = site_action_items.get(name)
    if action_cls.singleton:
        for registered_subject in registered_subject_cls.objects.all():
            try:
                action_item_cls.objects.get(
                    subject_identifier=registered_subject.subject_identifier,
                    action_type__name=name,
                )
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                try:
                    action_item_cls.objects.get(
                        subject_identifier=registered_subject.subject_identifier,
                        action_type__name=name,
                        status=CLOSED,
                    )
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    for index, action_item in enumerate(
                        action_item_cls.objects.filter(
                            subject_identifier=registered_subject.subject_identifier,
                            action_type__name=name,
                        )
                    ):
                        if index > 0:
                            action_item.delete()
                else:
                    action_item_cls.objects.filter(
                        subject_identifier=registered_subject.subject_identifier,
                        action_type__name=name,
                        status=NEW,
                    ).delete()


def fix_null_related_action_items2(delete_orphans=None):  # noqa
    """Used for early action items where related_action_item
    was not set, e.g. v0.1.1

    Call from shell.

    mysql:
        select action_identifier, subject_identifier,
        created from edc_action_item_actionitem
        where related_action_item_id is NULL
        and reference_model = 'ambition_ae.aefollowup';
    """
    from django.apps import apps as django_apps

    post_save.disconnect(dispatch_uid="serialize_on_save")
    pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")
    action_item_cls = django_apps.get_model("edc_action_item", "ActionItem")
    for action_cls in site_action_items.registry.values():
        if action_cls.related_reference_fk_attr:
            for action_item in action_item_cls.objects.filter(
                related_action_item__isnull=True, action_type__name=action_cls.name
            ):
                try:
                    action_item.reference_obj
                except ObjectDoesNotExist as e:
                    if delete_orphans:
                        print(f"Deleting orphaned action item {action_item}.")
                        action_item.delete()
                    else:
                        print(f"Skipping {action_item}. Got {e}")
                else:
                    print(
                        action_item,
                        action_cls.related_reference_fk_attr,
                        action_item.reference_obj,
                    )
                    action_item.related_action_item = getattr(
                        action_item.reference_obj, action_cls.related_reference_fk_attr
                    ).action_item
                    action_item.save()
