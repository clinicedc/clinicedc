from typing import Iterable, Protocol

from edc_crf.stubs import MetaModelStub


class SiteModelStub(Protocol):
    id: int
    name: str

    def all(self) -> Iterable:
        ...

    def add(self, obj) -> None:
        ...

    def clear(self) -> None:
        ...


class RoleModelStub(Protocol):
    name: str
    display_name: str
    display_index: str
    _meta: MetaModelStub

    def all(self) -> Iterable:
        ...

    def add(self, obj) -> None:
        ...

    def clear(self) -> None:
        ...

    def save(self, *args, **kwargs) -> None:
        ...


class UserProfileModelStub(Protocol):
    user: str
    sites: SiteModelStub
    job_title: str
    alternate_email: str
    clinic_label_printer: str
    lab_label_printer: str
    print_server: str
    export_format: str
    roles: RoleModelStub
    _meta: MetaModelStub

    def save(self, *args, **kwargs) -> None:
        ...


class UserModelStub(Protocol):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    mobile: str
    userprofile: UserProfileModelStub
    _meta: MetaModelStub

    def save(self, *args, **kwargs) -> None:
        ...

    def set_password(self, password):
        ...
