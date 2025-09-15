from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import requests
from django.conf import settings
from django.core.exceptions import ValidationError

from .utils import get_email_enabled

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from requests.models import Response


class EmailNotEnabledError(ValidationError):
    pass


class UserEmailError(ValidationError):
    pass


class MailingListManager:
    """A class to create (and update) mailing lists, subscribe,
    unsubscribe members, etc via the MAILGUN API.

    If this is a test / UAT, the mailing list names from settings
    are automatically prefixed with 'test'.
    """

    url = "https://api.mailgun.net/v3/lists"
    api_url_attr = "MAILGUN_API_URL"
    api_key_attr = "MAILGUN_API_KEY"

    def __init__(self, address: str = None, name: str = None, display_name: str = None):
        self._api_key: str | None = None
        self._api_url: str | None = None
        self.address = address  # mailing list address
        self.display_name = display_name
        self.email_enabled: bool = get_email_enabled()
        self.name = name

    @property
    def api_url(self) -> str | None:
        """Returns the api_url or None."""
        if not self._api_url:
            error_msg = (
                f"Email is enabled but API_URL is not set. See settings.{self.api_url_attr}"
            )
            try:
                self._api_url = getattr(settings, self.api_url_attr)
            except AttributeError:
                raise EmailNotEnabledError(error_msg, code="api_url_attribute_error")
            else:
                if not self._api_url:
                    raise EmailNotEnabledError(error_msg, code="api_url_is_none")
        return self._api_url

    @property
    def api_key(self) -> str | None:
        """Returns the api_key or None."""
        if not self._api_key:
            error_msg = (
                f"Email is enabled but API_KEY is not set. See settings.{self.api_key_attr}"
            )
            try:
                self._api_key = getattr(settings, self.api_key_attr)
            except AttributeError:
                raise EmailNotEnabledError(error_msg, code="api_key_attribute_error")
            else:
                if not self._api_key:
                    raise EmailNotEnabledError(error_msg, code="api_key_is_none")
        return self._api_key

    def subscribe(self, user: User, verbose: bool | None = None) -> Response:
        """Returns a response after attempting to subscribe
        a member to the list.
        """
        if not self.email_enabled:
            raise EmailNotEnabledError("Email is not enabled. See settings.EMAIL_ENABLED")
        if not user.email:
            raise UserEmailError(f"User {user}'s email address is not defined.")
        response = requests.post(
            f"{self.api_url}/{self.address}/members",
            auth=("api", self.api_key),
            data={
                "subscribed": True,
                "address": user.email,
                "name": f"{user.first_name} {user.last_name}",
                "description": f"{user.userprofile.job_title or ''}",
                "upsert": "yes",
            },
            timeout=10,
        )
        if verbose:
            self._output_response_message("subscribe", response)
        return response

    def unsubscribe(self, user, verbose: bool | None = None) -> Response:
        """Returns a response after attempting to unsubscribe
        a member from the list.
        """
        if not self.email_enabled:
            raise EmailNotEnabledError("Email is not enabled. See settings.EMAIL_ENABLED")
        response = requests.put(
            f"{self.api_url}/{self.address}/members/{user.email}",
            auth=("api", self.api_key),
            data={"subscribed": False},
            timeout=10,
        )
        if verbose:
            self._output_response_message("unsubscribe", response)
        return response

    def _output_response_message(self, action: str, response: Response) -> None:
        try:
            email = response.json()["member"]["address"]
            message = response.json()["message"]
            subscribed = response.json()["member"]["subscribed"]
        except KeyError:
            sys.stdout.write(
                f"{action.title()} failed. Got response={response.status_code} "
                f"{response.json()!s}"
            )
        else:
            sys.stdout.write(
                f"{action.title()} for {email} from {self.address} successful. "
                f"Got response={response.status_code}. {message} "
                f"subscribed={subscribed}.\n"
            )

    def create(self, verbose: bool | None = None) -> Response:
        """Returns a response after attempting to create the list."""
        if not self.email_enabled:
            raise EmailNotEnabledError("Email is not enabled. See settings.EMAIL_ENABLED")
        response = requests.post(
            self.api_url,
            auth=("api", self.api_key),
            data={
                "address": self.address,
                "name": self.name,
                "description": self.display_name,
            },
            timeout=10,
        )
        if verbose:
            sys.stdout.write(
                f"Creating mailing list {self.address}. Got response={response.status_code}.\n"
            )
        return response

    def delete(self) -> Response:
        """Returns a response after attempting to delete the list."""
        if not self.email_enabled:
            raise EmailNotEnabledError("Email is not enabled. See settings.EMAIL_ENABLED")
        return requests.delete(
            f"{self.api_url}/{self.address}", auth=("api", self.api_key), timeout=10
        )

    def delete_member(self, user: User) -> Response:
        """Returns a response after attempting to remove
        a member from the list.
        """
        if not self.email_enabled:
            raise EmailNotEnabledError("Email is not enabled. See settings.EMAIL_ENABLED")
        return requests.delete(
            f"{self.api_url}/{self.address}/members/{user.email}",
            auth=("api", self.api_key),
            timeout=10,
        )
