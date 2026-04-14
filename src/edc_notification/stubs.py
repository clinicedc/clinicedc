from datetime import datetime
from typing import Protocol


class BaseNotificationStub(Protocol):
    display_name: str | None
    email_body_template: str
    email_footer_template: str
    email_from: list[str]
    email_subject_template: str
    email_test_body_line: str
    email_to: list[str] | None
    name: str | None
    sms_template: str
    sms_test_line: str

    @property
    def default_email_to(self) -> list[str]: ...

    def notify(
        self,
        force_notify: bool | None = None,
        use_email: bool | None = None,
        use_sms: bool | None = None,
        email_body_template: str | None = None,
        **kwargs,
    ) -> bool: ...


class NotificationStub(BaseNotificationStub, Protocol): ...


class NotificationModelStub(BaseNotificationStub, Protocol):
    emailed: str
    emailed_datetime: datetime
    enabled: bool
    model: str
