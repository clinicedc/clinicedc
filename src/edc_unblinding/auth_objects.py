UNBLINDING_REQUESTORS_ROLE = "UNBLINDING_REQUESTORS_ROLE"
UNBLINDING_REVIEWERS_ROLE = "UNBLINDING_REVIEWERS_ROLE"

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
