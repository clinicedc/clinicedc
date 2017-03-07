from django.contrib import messages

from edc_base.utils import get_utcnow


def flag_as_verified_against_paper(modeladmin, request, queryset, **kwargs):
    """Flags instance as verified against the paper document.
    """
    for obj in queryset:
        obj.is_verified = True
        obj.is_verified_datetime = get_utcnow()
        obj.verified_by = request.user.username
        obj.save(update_fields=[
            'is_verified', 'is_verified_datetime', 'verified_by'])
        messages.add_message(
            request,
            messages.SUCCESS,
            '\'{}\' for \'{}\' has been verified against the paper document.'.format(
                obj._meta.verbose_name, obj.subject_identifier))


flag_as_verified_against_paper.short_description = "Verify against paper document"


def unflag_as_verified_against_paper(modeladmin, request, queryset, **kwargs):
    """Unflags instance as verified.
    """
    for obj in queryset:
        obj.is_verified = False
        obj.is_verified_datetime = None
        obj.verified_by = None
        obj.save(
            update_fields=['is_verified', 'is_verified_datetime', 'verified_by'])


unflag_as_verified_against_paper.short_description = "Un-verify"
