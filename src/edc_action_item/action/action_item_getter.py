from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class ActionItemGetterError(Exception):
    pass


class ActionItemObjectDoesNotExist(ObjectDoesNotExist):
    pass


class ActionItemParentDoesNotExist(ObjectDoesNotExist):
    pass


class ActionItemMismatch(Exception):
    pass


class ActionItemGetter:

    model = 'edc_action_item.actionitem'

    def __init__(self, action_cls,
                 action_identifier=None,
                 subject_identifier=None,
                 reference_identifier=None,
                 parent_reference_identifier=None,
                 allow_create=None):

        if action_cls.parent_reference_model_fk_attr:
            # if fk, parent_reference model obj must exist
            try:
                action_cls.parent_reference_model_cls().objects.get(
                    subject_identifier=subject_identifier,
                    tracking_identifier=parent_reference_identifier)
            except ObjectDoesNotExist as e:
                raise ActionItemParentDoesNotExist(
                    f'ActionItem parent does not exist. '
                    f'{parent_reference_identifier}. Got {e}.')

        opts = dict(
            action_type=action_cls.action_type(),
            reference_identifier=reference_identifier,
            parent_reference_identifier=parent_reference_identifier)

        if not reference_identifier:
            del opts['reference_identifier']
            opts.update(reference_identifier__isnull=True)
        if not parent_reference_identifier:
            del opts['parent_reference_identifier']
            opts.update(parent_reference_identifier__isnull=True)

        self.model_obj = None
        try:
            self.model_obj = self.model_cls().objects.get(
                action_identifier=action_identifier)
        except ObjectDoesNotExist:
            if not subject_identifier:
                raise TypeError(
                    f'Subject identifier cannot be None. Got {opts}. See {action_cls}.')
            try:
                self.model_obj = self.model_cls().objects.get(
                    subject_identifier=subject_identifier, **opts)
            except ObjectDoesNotExist:
                if reference_identifier:
                    del opts['reference_identifier']
                    opts.update(reference_identifier__isnull=True)
                try:
                    self.model_obj = self.model_cls().objects.get(
                        subject_identifier=subject_identifier, **opts)
                except ObjectDoesNotExist:
                    pass
                except MultipleObjectsReturned:
                    if (not parent_reference_identifier
                            and action_cls.parent_reference_model_fk_attr):
                        raise
                    self.model_obj = self.model_cls().objects.filter(
                        subject_identifier=subject_identifier, **opts).first()
            except MultipleObjectsReturned:
                raise
            if not self.model_obj and allow_create:
                self.model_obj = self.model_cls().objects.create(
                    subject_identifier=subject_identifier,
                    action_type=action_cls.action_type(),
                    reference_identifier=reference_identifier,
                    parent_reference_identifier=parent_reference_identifier)
        else:
            subject_identifier = self.model_obj.subject_identifier
            reference_identifier = self.model_obj.reference_identifier
            parent_reference_identifier = self.model_obj.parent_reference_identifier
        if not self.model_obj:
            raise ActionItemObjectDoesNotExist(
                f'Action item does not exists. Got action_cls={repr(action_cls)} using '
                f'\n(action_identifier={action_identifier},\n'
                f'subject_identifier={subject_identifier},\n'
                f'reference_identifier={reference_identifier},\n'
                f'action_type={action_cls.action_type()}).\n')
        self.action_identifier = self.model_obj.action_identifier

    @classmethod
    def model_cls(cls):
        return django_apps.get_model(cls.model)
