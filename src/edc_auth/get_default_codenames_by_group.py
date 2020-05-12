from .codenames import (
    account_manager,
    administration,
    ae,
    ae_review,
    auditor,
    celery_manager,
    clinic,
    data_manager,
    data_query,
    dispensing,
    everyone,
    export,
    export_rando,
    lab,
    lab_view,
    pharmacy,
    pii,
    pii_view,
    get_rando,
    review,
    site_data_manager,
    tmg,
)
from .group_names import (
    AE,
    AE_REVIEW,
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CELERY_MANAGER,
    CLINIC,
    DATA_MANAGER,
    DATA_QUERY,
    DISPENSING,
    EVERYONE,
    EXPORT,
    EXPORT_RANDO,
    LAB,
    LAB_VIEW,
    PHARMACY,
    PII,
    PII_VIEW,
    RANDO,
    REVIEW,
    SITE_DATA_MANAGER,
    TMG,
)


def get_default_codenames_by_group():
    dct = {
        AE: ae,
        AE_REVIEW: ae_review,
        ACCOUNT_MANAGER: account_manager,
        ADMINISTRATION: administration,
        AUDITOR: auditor,
        CELERY_MANAGER: celery_manager,
        CLINIC: clinic,
        DATA_MANAGER: data_manager,
        DATA_QUERY: data_query,
        DISPENSING: dispensing,
        EVERYONE: everyone,
        EXPORT: export,
        EXPORT_RANDO: export_rando,
        LAB: lab,
        LAB_VIEW: lab_view,
        PHARMACY: pharmacy,
        PII: pii,
        PII_VIEW: pii_view,
        RANDO: get_rando,
        REVIEW: review,
        SITE_DATA_MANAGER: site_data_manager,
        TMG: tmg,
    }

    codenames_by_group = {}
    for k, v in dct.items():
        try:
            codenames_by_group.update({k: v()})
        except TypeError:
            codenames_by_group.update({k: v})
    return codenames_by_group
