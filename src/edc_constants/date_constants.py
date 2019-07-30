from django.conf import settings

# for strftime formatting in edc messages etc.

timezone = " %Z" if settings.USE_TZ else ""
try:
    EDC_DATE_FORMAT = settings.EDC_DATE_FORMAT
except AttributeError:
    EDC_DATE_FORMAT = "%A %d %b %Y"

try:
    EDC_DATETIME_FORMAT = settings.EDC_DATETIME_FORMAT
except AttributeError:
    EDC_DATETIME_FORMAT = f"%A %d %b %Y %I:%M%p{timezone}"

try:
    EDC_SHORT_DATE_FORMAT = settings.EDC_SHORT_DATE_FORMAT
except AttributeError:
    EDC_SHORT_DATE_FORMAT = "%Y-%m-%d"

try:
    EDC_SHORT_DATETIME_FORMAT = settings.EDC_SHORT_DATETIME_FORMAT
except AttributeError:
    EDC_SHORT_DATETIME_FORMAT = f"%Y-%m-%d %H:%M{timezone}"
