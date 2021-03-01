from typing import Optional, Protocol, Type
from uuid import UUID

from django.db import models


class ActionStub(Protocol):
    def __init__(
        self,
        action_item: Optional["ActionItemStub"] = None,
        reference_obj: Optional[models.Model] = None,
        subject_identifier: str = None,
        action_identifier: str = None,
        parent_action_item: Optional["ActionItemStub"] = None,
        related_action_item: Optional["ActionItemStub"] = None,
        using: Optional[str] = None,
        readonly: Optional[bool] = None,
    ) -> None:
        ...

    name: str
    action_item: "ActionItemStub"
    action_identifier: str
    related_reference_model: Optional[str]
    related_reference_fk_attr: Optional[str]
    subject_identifier: str
    related_action_item: Optional["ActionItemStub"]
    ...


class ActionTypeStub(Protocol):
    name: str
    display_name: str
    reference_model: Optional[str]
    related_reference_model: Optional[str]
    ...


class ActionItemStub(Protocol):
    id: UUID
    action_name: str
    action_item_model: str
    subject_dashboard_url: str
    action_identifier: str
    action_item: "ActionItemStub"
    action_type: ActionTypeStub
    linked_to_reference: bool
    parent_action_item: Optional["ActionItemStub"]
    related_action_item: Optional["ActionItemStub"]
    subject_identifier: str
    action_item_reason: str

    action_cls: ActionStub

    def get_status_display(self) -> str:
        ...

    def get_action_cls(self) -> Type[ActionStub]:
        ...


class ActionItemWithNotificationStub(ActionItemStub, Protocol):
    notification_email_to: str
    notification_display_name: str
    notification_fields: list
    notify_on_changed_reference_obj: bool = True
    notify_on_close: bool = False
    notify_on_new: bool = False
    notify_on_new_and_no_reference_obj: bool = True
    notify_on_open: bool = False
    ...
