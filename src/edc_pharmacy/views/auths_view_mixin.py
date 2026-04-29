from django.core.exceptions import PermissionDenied
from edc_auth.constants import CLINICIAN_ROLE, CLINICIAN_SUPER_ROLE

from ..auth_objects import PHARMACIST_ROLE, PHARMACY_SUPER_ROLE, SITE_PHARMACIST_ROLE


def user_has_pharmacist_role(user) -> bool:
    """True if the user has PHARMACIST_ROLE."""
    if not user.is_authenticated:
        return False
    return PHARMACIST_ROLE in [r.name for r in user.userprofile.roles.all()]


class AuthsViewMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            roles=[obj.name for obj in self.request.user.userprofile.roles.all()],
            SITE_PHARMACIST_ROLE=SITE_PHARMACIST_ROLE,
            PHARMACIST_ROLE=PHARMACIST_ROLE,
            PHARMACY_SUPER_ROLE=PHARMACY_SUPER_ROLE,
            CLINICIAN_ROLE=CLINICIAN_ROLE,
            CLINICIAN_SUPER_ROLE=CLINICIAN_SUPER_ROLE,
        )
        return context


class PharmacistRequiredMixin(AuthsViewMixin):
    """Restricts access to users with PHARMACIST_ROLE.

    Mix this in (in place of AuthsViewMixin) on any view that exposes the
    central order / receive workflow, including blinding-sensitive details
    like assignment and batch number on the printed Purchase Order.
    """

    def dispatch(self, request, *args, **kwargs):
        if not user_has_pharmacist_role(request.user):
            raise PermissionDenied(
                f"The {PHARMACIST_ROLE} role is required to access the "
                "order and receive workflow."
            )
        return super().dispatch(request, *args, **kwargs)
