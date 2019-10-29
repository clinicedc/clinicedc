from .default_codenames_by_group import default_codenames_by_group
from .group_names import (
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AE,
    AE_REVIEW,
    AUDITOR,
    CELERY_MANAGER,
    CLINIC,
    DATA_MANAGER,
    DATA_QUERY,
    EVERYONE,
    EXPORT,
    LAB,
    LAB_VIEW,
    PHARMACY,
    PII,
    PII_VIEW,
    RANDO,
    REVIEW,
    SCREENING,
    SITE_DATA_MANAGER,
    TMG,
    UNBLINDING_REVIEWERS,
    UNBLINDING_REQUESTORS,
)

codenames_by_group = {k: v for k, v in default_codenames_by_group.items()}


def slugify_user(user):
    return f"{user.first_name}-{user.last_name}-{user.username}-{user.email}"
