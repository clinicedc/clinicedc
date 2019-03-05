import arrow
import sys

from dateutil.relativedelta import relativedelta
from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.conf import settings

style = color_style()


class ArrowObject:
    def __init__(self, open_dt, close_dt):
        self.ropen = arrow.Arrow.fromdatetime(open_dt, open_dt.tzinfo).to("utc")
        self.rclose = arrow.Arrow.fromdatetime(close_dt, close_dt.tzinfo).to("utc")


class AppConfig(DjangoAppConfig):
    name = "edc_protocol"
    verbose_name = "Edc Protocol"

    # set with example defaults, you will need to change from your project
    protocol = "AAA000"
    protocol_number = "000"  # 3 digits, used for identifiers
    protocol_name = "My Protocol"
    protocol_title = "My Protocol of Many Things"
    try:
        email_contacts = settings.EMAIL_CONTACTS
    except AttributeError:
        email_contacts = {}
    study_open_datetime = arrow.utcnow().floor("hour") - relativedelta(years=1)
    study_close_datetime = arrow.utcnow().ceil("hour")
    messages_written = False

    def ready(self):
        # from .site_protocol_subjects import site_protocol_subjects

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" * {self.protocol}: {self.protocol_name}.\n")
        self.rstudy_open = (
            arrow.Arrow.fromdatetime(
                self.study_open_datetime, self.study_open_datetime.tzinfo
            )
            .to("utc")
            .floor("hour")
        )
        self.rstudy_close = (
            arrow.Arrow.fromdatetime(
                self.study_close_datetime, self.study_close_datetime.tzinfo
            )
            .to("utc")
            .ceil("hour")
        )

        self.study_open_datetime = self.rstudy_open.datetime
        self.study_close_datetime = self.rstudy_close.datetime

        open_date = self.study_open_datetime.strftime("%Y-%m-%d %Z")
        sys.stdout.write(f" * Study opening date: {open_date}\n")
        close_date = self.study_close_datetime.strftime("%Y-%m-%d %Z")
        sys.stdout.write(f" * Expected study closing date: {close_date}\n")

        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        sys.stdout.flush()
        self.messages_written = True

    @property
    def arrow(self):
        return ArrowObject(self.study_open_datetime, self.study_close_datetime)
