from datetime import datetime
from typing import List, Protocol


class BaseNotificationStub(Protocol):
    display_name: str | None
    email_body_template: str
    email_footer_template: str
    email_from: list[str]
    # email_message_cls = Type[EmailMessage]
    email_subject_template: str
    email_test_body_line: str
    email_to: list[str] | None
    name: str | None
    # sms_client: Type[Client]
    sms_template: str
    sms_test_line: str

    @property
    def default_email_to(self) -> List[str]: ...  # noqa

    def notify(
        self,
        force_notify: bool = None,
        use_email: bool = None,
        use_sms: bool = None,
        email_body_template: str = None,
        **kwargs,
    ) -> bool: ...


class NotificationStub(BaseNotificationStub, Protocol): ...


class NotificationModelStub(BaseNotificationStub, Protocol):
    emailed: str
    emailed_datetime: datetime
    enabled: bool
    model: str
