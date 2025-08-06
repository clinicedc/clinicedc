from edc_auth.constants import CLINICIAN_ROLE, CLINICIAN_SUPER_ROLE

from ..auth_objects import PHARMACIST_ROLE, PHARMACY_SUPER_ROLE, SITE_PHARMACIST_ROLE


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
