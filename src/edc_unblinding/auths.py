from contextlib import suppress

from edc_auth.site_auths import GroupAlreadyExists, RoleAlreadyExists, site_auths

from .auth_objects import (
    UNBLINDING_REQUESTORS,
    UNBLINDING_REQUESTORS_ROLE,
    UNBLINDING_REVIEWERS,
    UNBLINDING_REVIEWERS_ROLE,
    unblinding_requestors,
    unblinding_reviewers,
)


def update_site_auths() -> None:
    with suppress(GroupAlreadyExists):
        site_auths.add_group(*unblinding_requestors, name=UNBLINDING_REQUESTORS)
    with suppress(GroupAlreadyExists):
        site_auths.add_group(*unblinding_reviewers, name=UNBLINDING_REVIEWERS)
    with suppress(RoleAlreadyExists):
        site_auths.add_role(UNBLINDING_REQUESTORS, name=UNBLINDING_REQUESTORS_ROLE)
    with suppress(RoleAlreadyExists):
        site_auths.add_role(UNBLINDING_REVIEWERS, name=UNBLINDING_REVIEWERS_ROLE)


update_site_auths()
