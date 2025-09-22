from ..constants import (
    ACCOUNT_MANAGER,
    ACCOUNT_MANAGER_ROLE,
    ADMINISTRATION,
    AUDITOR,
    AUDITOR_ROLE,
    CLINIC,
    CLINIC_SUPER,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    CUSTOM_ROLE,
    EVERYONE,
    NURSE_ROLE,
    PII,
    PII_VIEW,
    STAFF_ROLE,
    STATISTICIAN,
)


def get_default_roles() -> dict[str, list[str]]:
    """Format {ROLE_NAME: [GROUP_NAME, GROUP_NAME, ...]"""
    return {
        ACCOUNT_MANAGER_ROLE: [ACCOUNT_MANAGER],
        AUDITOR_ROLE: [
            AUDITOR,
            PII_VIEW,
        ],
        CLINICIAN_ROLE: [
            CLINIC,
            PII,
        ],
        CLINICIAN_SUPER_ROLE: [
            CLINIC_SUPER,
            CLINIC,
            PII,
        ],
        CUSTOM_ROLE: [],
        NURSE_ROLE: [
            CLINIC,
            PII,
        ],
        STAFF_ROLE: [ADMINISTRATION, EVERYONE],
        STATISTICIAN: [AUDITOR],
    }
