from edc_auth.site_auths import site_auths

from .auth_objects import (
    EDC_DX_REVIEW,
    EDC_DX_REVIEW_SUPER,
    EDC_DX_REVIEW_VIEW,
    codenames,
)

site_auths.add_group(*codenames, name=EDC_DX_REVIEW_VIEW, view_only=True)
site_auths.add_group(*codenames, name=EDC_DX_REVIEW, no_delete=True)
site_auths.add_group(*codenames, name=EDC_DX_REVIEW_SUPER)
