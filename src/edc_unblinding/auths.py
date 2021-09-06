from edc_auth.constants import CLINICIAN_ROLE, NURSE_ROLE, TMG_ROLE
from edc_auth.site_auths import site_auths

UNBLINDING_REQUESTORS = "UNBLINDING_REQUESTORS"
UNBLINDING_REVIEWERS = "UNBLINDING_REVIEWERS"

unblinding_requestors = [
    "edc_unblinding.add_unblindingrequest",
    "edc_unblinding.change_unblindingrequest",
    "edc_unblinding.delete_unblindingrequest",
    "edc_unblinding.view_unblindingrequest",
    "edc_unblinding.view_historicalunblindingrequest",
    "edc_unblinding.view_unblindingrequestoruser",
]


unblinding_reviewers = [
    "edc_unblinding.add_unblindingreview",
    "edc_unblinding.change_unblindingreview",
    "edc_unblinding.delete_unblindingreview",
    "edc_unblinding.view_unblindingreview",
    "edc_unblinding.view_historicalunblindingreview",
    "edc_unblinding.view_unblindingrevieweruser",
]

groups_by_role_name = {
    UNBLINDING_REQUESTORS: unblinding_requestors,
    UNBLINDING_REVIEWERS: unblinding_reviewers,
}

role_names = {
    UNBLINDING_REQUESTORS: "Unblinding requestors",
    UNBLINDING_REVIEWERS: "Unblinding reviewers",
}

site_auths.register(groups_by_role_name=groups_by_role_name, role_names=role_names)
site_auths.add_to_role(CLINICIAN_ROLE, unblinding_requestors)
site_auths.add_to_role(NURSE_ROLE, unblinding_requestors)
site_auths.add_to_role(TMG_ROLE, unblinding_reviewers)
