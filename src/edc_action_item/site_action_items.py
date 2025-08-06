from __future__ import annotations

import copy
import sys
from dataclasses import InitVar, dataclass, field
from importlib import import_module
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule
from edc_notification.site_notifications import (
    AlreadyRegistered as NotificationAlreadyRegistered,
)
from edc_notification.site_notifications import site_notifications
from edc_prn.prn import Prn
from edc_prn.site_prn_forms import AlreadyRegistered as PrnAlreadyRegistered
from edc_prn.site_prn_forms import site_prn_forms

from .create_or_update_action_type import create_or_update_action_type
from .get_action_type import get_action_type

if TYPE_CHECKING:
    from .action import Action
    from .action_with_notification import ActionWithNotification


class AlreadyRegistered(Exception):
    pass


class SiteActionError(Exception):
    pass


@dataclass
class ActionButton:
    action_cls: InitVar[Type[Action] | Type[ActionWithNotification]] = None
    name: str = field(init=False)
    display_name: str = field(init=False)
    action_type_id: str = field(init=False)

    def __post_init__(self, action_cls: Type[Action] | Type[ActionWithNotification]):
        self.name = action_cls.name
        self.display_name = action_cls.display_name
        self.action_type_id = str(get_action_type(action_cls).pk)


class SiteActionItemCollection:
    def __init__(self):
        self.registry: dict[str, Type[Action] | Type[ActionWithNotification]] = {}
        self.updated_action_types: bool | None = None
        prn = Prn(model="edc_action_item.actionitem", url_namespace="edc_action_item_admin")
        site_prn_forms.register(prn)

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __len__(self):
        return len(self.registry.values())

    def __iter__(self):
        return iter(self.registry.values())

    def unregister(self, action_cls: Type[Action] | Type[ActionWithNotification]) -> None:
        if action_cls.name in self.registry:
            del self.registry[action_cls.name]
            prn = Prn(
                model=action_cls.get_reference_model(),
                url_namespace=action_cls.admin_site_name,
            )
            site_prn_forms.unregister(prn)

    def register(self, action_cls: Type[Action] | Type[ActionWithNotification] = None) -> None:
        if action_cls.name in self.registry:
            raise AlreadyRegistered(
                f"Action class is already registered. Got name='{action_cls.name}' "
                f"for {action_cls.__name__}"
            )
        else:
            self.registry.update({action_cls.name: action_cls})
        if action_cls.show_link_to_changelist:
            prn = Prn(
                model=action_cls.get_reference_model(),
                url_namespace=action_cls.admin_site_name,
            )
            try:
                site_prn_forms.register(prn)
            except PrnAlreadyRegistered:
                pass
        try:
            action_cls.notification_email_to
        except AttributeError:
            pass
        else:
            self.register_notifications(action_cls)

    @staticmethod
    def register_notifications(action_cls: Type[Action] | Type[ActionWithNotification]):
        """Registers a new model notification and an updated model
        notification for this action cls.

        See edc_notification.
        """
        if action_cls.notification_cls():
            try:
                site_notifications.register(action_cls.notification_cls())
            except NotificationAlreadyRegistered:
                pass

    @property
    def all(self) -> dict[str, Type[Action] | Type[ActionWithNotification]]:
        return self.registry

    def get(self, name) -> Type[Action] | Type[ActionWithNotification]:
        """Returns an action class."""
        if name not in self.registry:
            raise SiteActionError(
                f"Action does not exist. Did you register the Action? "
                f"Expected one of {self.registry}. Got {name}."
            )
        return self.registry.get(name)

    def get_by_model(self, model=None) -> Type[Action] | Type[ActionWithNotification] | None:
        """Returns the action_cls linked to this reference model."""
        for action_cls in self.registry.values():
            if action_cls.get_reference_model() == model:
                return self.get(action_cls.name)
        return None

    def get_add_actions_to_show(self) -> dict[str, Type[Action]]:
        actions = {
            action_cls.name: action_cls
            for action_cls in self.registry.values()
            if action_cls.show_link_to_add
        }
        return actions

    def create_or_update_action_types(self) -> None:
        """Populates the ActionType model."""
        for action_cls in self.registry.values():
            create_or_update_action_type(**action_cls.as_dict())
        self.updated_action_types = True

    @staticmethod
    def autodiscover(module_name=None, verbose=True):
        before_import_registry = {}
        module_name = module_name or "action_items"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_action_items.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f"   - registered '{module_name}' from '{app}'\n")
                except SiteActionError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_action_items.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteActionError(str(e))
            except ImportError:
                pass
            # except Exception as e:
            #     raise SiteActionError(
            #         f"{e.__class__.__name__} was raised when loading {module_name}. "
            #         f'Got "{e}" See {app}.{module_name}'
            #     )


site_action_items = SiteActionItemCollection()
