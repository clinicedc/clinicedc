from django.contrib import messages
from edc_utils import get_utcnow


def verify_consent(request=None, consent_obj=None):
    if consent_obj.is_verified:
        return None
    else:
        consent_obj.is_verified = True
        consent_obj.is_verified_datetime = get_utcnow()
        consent_obj.verified_by = request.user.username
        consent_obj.save(update_fields=["is_verified", "is_verified_datetime", "verified_by"])
    return consent_obj


def unverify_consent(consent_obj=None):
    consent_obj.is_verified = False
    consent_obj.is_verified_datetime = None
    consent_obj.verified_by = None
    consent_obj.save(update_fields=["is_verified", "is_verified_datetime", "verified_by"])
    return consent_obj


def flag_as_verified_against_paper(modeladmin, request, queryset, **kwargs):  # noqa
    """Flags instance as verified against the paper document."""
    for consent_obj in queryset:
        if not consent_obj.open_data_queries.count() > 0:
            if verify_consent(request, consent_obj):
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"'{consent_obj._meta.verbose_name}' for ' "
                    f"{consent_obj.subject_identifier}' "
                    f"has been verified against the paper document.",
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                f"'{consent_obj._meta.verbose_name}' for ' "
                f"{consent_obj.subject_identifier}' "
                f"has open data queries.",
            )


flag_as_verified_against_paper.short_description = "Verify consent against paper document"


def unflag_as_verified_against_paper(modeladmin, request, queryset, **kwargs):  # noqa
    """Unflags instance as verified."""
    for consent_obj in queryset:
        unverify_consent(consent_obj)


# noinspection PyTypeHints
unflag_as_verified_against_paper.short_description = "Unverify consent"  # type:ignore
