from clinicedc_constants import (
    AE,
    AE_REVIEW,
    AE_SUPER,
    TMG,
    TMG_REVIEW,
)

from edc_action_item.auth_objects import (
    ACTION_ITEM,
    ACTION_ITEM_EXPORT,
    ACTION_ITEM_VIEW_ONLY,
)
from edc_appointment.auth_objects import (
    APPOINTMENT,
    APPOINTMENT_EXPORT,
    APPOINTMENT_VIEW,
)
from edc_auth.constants import (
    AUDITOR,
    AUDITOR_ROLE,
    CLINIC,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
    TMG_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import (
    DATA_MANAGER_EXPORT,
    DATA_MANAGER_ROLE,
    SITE_DATA_MANAGER_ROLE,
)
from edc_export.constants import DATA_EXPORTER_ROLE
from edc_label.auth_objects import LABELING
from edc_offstudy.auth_objects import OFFSTUDY
from edc_pharmacy.auth_objects import PHARMACIST_ROLE, SITE_PHARMACIST_ROLE
from edc_qareports.auth_objects import (
    QA_REPORTS,
    QA_REPORTS_AUDIT,
    QA_REPORTS_AUDIT_ROLE,
    QA_REPORTS_ROLE,
)
from edc_randomization.auth_objects import RANDO_BLINDED, RANDO_UNBLINDED
from edc_screening.auth_objects import SCREENING, SCREENING_SUPER, SCREENING_VIEW
from edc_unblinding.auth_objects import UNBLINDING_REQUESTORS

from .auth_objects import (
    DEMO_AUDITOR,
    DEMO_CLINIC,
    DEMO_CLINIC_SUPER,
    DEMO_REPORTS,
    DEMO_REPORTS_AUDIT,
    clinic_codenames,
    reports_codenames,
    screening_codenames,
)

site_auths.add_group(*reports_codenames, name=DEMO_REPORTS)
site_auths.add_group(*reports_codenames, name=DEMO_REPORTS_AUDIT, view_only=True)

# screening
site_auths.update_group(*screening_codenames, name=SCREENING_SUPER)
site_auths.update_group(*screening_codenames, name=SCREENING_VIEW, view_only=True)
site_auths.update_group(*screening_codenames, name=SCREENING, no_delete=True)

# demo groups
site_auths.add_group(*clinic_codenames, name=DEMO_AUDITOR, view_only=True)
site_auths.add_group(*clinic_codenames, name=DEMO_CLINIC, no_delete=True)
site_auths.add_group(*clinic_codenames, name=DEMO_CLINIC_SUPER)

# update edc roles
site_auths.update_role(
    ACTION_ITEM,
    AE,
    APPOINTMENT,
    DEMO_CLINIC,
    DEMO_REPORTS,
    QA_REPORTS,
    SCREENING,
    UNBLINDING_REQUESTORS,
    name=CLINICIAN_ROLE,
)

site_auths.update_role(
    ACTION_ITEM,
    AE_SUPER,
    APPOINTMENT,
    DEMO_CLINIC_SUPER,
    DEMO_REPORTS,
    QA_REPORTS,
    SCREENING_SUPER,
    UNBLINDING_REQUESTORS,
    name=CLINICIAN_SUPER_ROLE,
)

site_auths.update_role(
    ACTION_ITEM,
    AE,
    APPOINTMENT,
    DEMO_CLINIC,
    DEMO_REPORTS,
    QA_REPORTS,
    SCREENING,
    name=NURSE_ROLE,
)

site_auths.update_role(
    ACTION_ITEM,
    AE,
    APPOINTMENT,
    CLINIC,
    LABELING,
    DEMO_CLINIC,
    DEMO_REPORTS,
    OFFSTUDY,
    QA_REPORTS,
    SCREENING_SUPER,
    TMG,
    name=DATA_MANAGER_ROLE,
)

site_auths.update_role(ACTION_ITEM, UNBLINDING_REQUESTORS, name=TMG_ROLE)

site_auths.update_role(
    ACTION_ITEM_VIEW_ONLY,
    AE_REVIEW,
    APPOINTMENT_VIEW,
    DEMO_AUDITOR,
    DEMO_REPORTS_AUDIT,
    QA_REPORTS_AUDIT,
    SCREENING_VIEW,
    TMG_REVIEW,
    name=AUDITOR_ROLE,
)

site_auths.update_role(
    AUDITOR,
    ACTION_ITEM,
    AE_REVIEW,
    DEMO_AUDITOR,
    SCREENING_VIEW,
    TMG_REVIEW,
    name=SITE_DATA_MANAGER_ROLE,
)


# data export
site_auths.update_role(
    ACTION_ITEM_EXPORT,
    APPOINTMENT_EXPORT,
    DATA_MANAGER_EXPORT,
    name=DATA_EXPORTER_ROLE,
)

site_auths.update_role(RANDO_UNBLINDED, name=PHARMACIST_ROLE)
site_auths.update_role(RANDO_BLINDED, name=SITE_PHARMACIST_ROLE)
site_auths.update_role(DEMO_REPORTS, name=QA_REPORTS_ROLE)
site_auths.update_role(DEMO_REPORTS_AUDIT, name=QA_REPORTS_AUDIT_ROLE)
