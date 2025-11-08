from __future__ import annotations

import socket
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.mail.message import EmailMessage
from django.utils import timezone
from edc_notification.utils import get_email_contacts
from edc_protocol.research_protocol_config import ResearchProtocolConfig

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class FilesEmailerError(ValidationError):
    pass


class FilesEmailer:
    def __init__(
        self,
        path_to_files: Path,
        *,
        file_ext: str,
        user: User,
        export_filenames: list[str],
        verbose: bool | None = None,
    ):
        self.path_to_files = path_to_files
        self.file_ext = file_ext
        self.user = user
        self.export_filenames = export_filenames
        self.verbose = verbose

        self.summary = [str(x) for x in self.export_filenames]
        self.summary.sort()
        self.emailed_to = self.user.email

        self.email_files()

        self.emailed_datetime = timezone.now()

    def email_files(self) -> None:
        email_message = self.get_email_message()
        files = [f for f in self.path_to_files.iterdir() if f.suffix == self.file_ext]
        x = 0
        index = 0
        for index, file in enumerate(files):
            email_message.attach_file(str(file))
            x += 1
            if x >= 10:
                email_message.subject = (
                    f"{email_message.subject} (items "
                    f"{index + 2 - x}-{index + 1} of {len(files)})"
                )
                self.send(email_message)
                email_message = self.get_email_message()
                x = 0
        if x > 0:
            email_message.subject = (
                f"{email_message.subject} (items {index + 2 - x}-{index + 1} of {len(files)})"
            )
            self.send(email_message)
        if self.verbose:
            sys.stdout.write(f"\nEmailed export files to {self.user.email}.\n")

    def get_email_message(self) -> EmailMessage:
        body = [
            f"Hello {self.user.first_name or self.user.username}",
            "The data you requested are attached.",
            (
                "An email can contain no more than 10 attached files. If you selected \n"
                "more than 10 tables for export, you will receive more than one email for \n"
                "this request."
            ),
            (
                "Tables with zero records are not exported so the total number of attached \n"
                "files may be fewer than the number of tables you originally selected."
            ),
            (
                "When importing files into your software note that the data are delimited \n"
                'by a pipe, "|",  instead of a comma. You will need to indicate this when you \n'  # noqa
                "open/import the files into Excel, Numbers or whichever software "
                "you are using."
            ),
            "Your request includes the following data:",
            f"{self.summary}",
            "Thanks",
        ]
        return EmailMessage(
            subject=f"{ResearchProtocolConfig().protocol_name.title()} trial data request",
            body="\n\n".join(body),
            from_email=get_email_contacts("data_request"),
            to=[self.user.email],
        )

    @staticmethod
    def send(email_message) -> None:
        try:
            email_message.send()
        except socket.gaierror as e:
            raise FilesEmailerError(
                "Unable to connect to email server.", code="gaierror"
            ) from e
