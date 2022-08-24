from django.conf import settings

from .constants import (
    ABNORMAL,
    CANCELLED,
    CLOSED,
    COMPLETE,
    FEMALE,
    INCOMPLETE,
    LIVE,
    MALE,
    NEW,
    NO,
    NOT_APPLICABLE,
    OPEN,
    OTHER,
    PENDING,
    TBD,
    TEST,
    UNKNOWN,
    YES,
)


def constants(request) -> dict:
    return dict(
        ABNORMAL=ABNORMAL,
        CANCELLED=CANCELLED,
        CLOSED=CLOSED,
        COMPLETE=COMPLETE,
        DEBUG=settings.DEBUG,
        FEMALE=FEMALE,
        INCOMPLETE=INCOMPLETE,
        LIVE=LIVE,
        MALE=MALE,
        NEW=NEW,
        NO=NO,
        NOT_APPLICABLE=NOT_APPLICABLE,
        OPEN=OPEN,
        OTHER=OTHER,
        PENDING=PENDING,
        SITE_ID=settings.SITE_ID,
        TBD=TBD,
        TEST=TEST,
        UNKNOWN=UNKNOWN,
        YES=YES,
    )
