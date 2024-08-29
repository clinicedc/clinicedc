from edc_lab import RequisitionPanel

from .constants import (
    BLOOD_GLUCOSE,
    BLOOD_GLUCOSE_POC,
    CD4,
    CHEMISTRY_LFT,
    CHEMISTRY_LIPIDS,
    CHEMISTRY_RFT,
    CHOL,
    FBC,
    HBA1C,
    HBA1C_POC,
    HDL,
    INSULIN,
    LDL,
    LFT,
    LIPIDS,
    RFT,
    SPUTUM,
    TRIG,
    VL,
)
from .processing_profiles import (
    blood_glucose_processing,
    cd4_processing,
    fbc_processing,
    hba1c_processing,
    insulin_processing,
    lft_processing,
    lipids_processing,
    poc_processing,
    rft_processing,
    sputum_processing,
    vl_processing,
)

hba1c_panel = RequisitionPanel(
    name=HBA1C,
    verbose_name="HbA1c (Venous)",
    processing_profile=hba1c_processing,
    abbreviation="HBA1C",
    utest_ids=[("hba1c", "HbA1c")],
)

hba1c_poc_panel = RequisitionPanel(
    name=HBA1C_POC,
    verbose_name="HbA1c (POC)",
    abbreviation="HBA1C_POC",
    processing_profile=poc_processing,
    utest_ids=[("hba1c", "HbA1c")],
)


fbc_panel = RequisitionPanel(
    name=FBC,
    verbose_name="Full Blood Count",
    processing_profile=fbc_processing,
    abbreviation="FBC",
    utest_ids=[
        ("haemoglobin", "Haemoglobin"),
        "hct",
        "rbc",
        "wbc",
        "platelets",
        "mcv",
        "mch",
        "mchc",
    ],
)

blood_glucose_panel = RequisitionPanel(
    name=BLOOD_GLUCOSE,
    verbose_name="Blood Glucose (Venous)",
    abbreviation="BGL",
    processing_profile=blood_glucose_processing,
    utest_ids=[("glucose", "Glucose")],
)

blood_glucose_poc_panel = RequisitionPanel(
    name=BLOOD_GLUCOSE_POC,
    verbose_name="Blood Glucose (POC)",
    abbreviation="BGL-POC",
    processing_profile=poc_processing,
    utest_ids=[("glucose", "Glucose")],
)

cd4_panel = RequisitionPanel(
    name=CD4,
    verbose_name="CD4",
    abbreviation="CD4",
    processing_profile=cd4_processing,
    utest_ids=["cd4"],
)
vl_panel = RequisitionPanel(
    name=VL,
    verbose_name="Viral Load",
    abbreviation="VL",
    processing_profile=vl_processing,
    utest_ids=["vl"],
)


rft_panel = RequisitionPanel(
    name=CHEMISTRY_RFT,
    verbose_name="Chemistry: Renal Function Tests",
    abbreviation=RFT,
    processing_profile=rft_processing,
    utest_ids=["urea", "creatinine", "uric_acid", "egfr", "egfr_drop"],
)

lipids_panel = RequisitionPanel(
    name=CHEMISTRY_LIPIDS,
    verbose_name="Chemistry: Lipids",
    abbreviation=LIPIDS,
    processing_profile=lipids_processing,
    utest_ids=[LDL, HDL, TRIG, CHOL],
)

lft_panel = RequisitionPanel(
    name=CHEMISTRY_LFT,
    verbose_name="Chemistry: Liver Function Tests",
    abbreviation=LFT,
    processing_profile=lft_processing,
    utest_ids=["ast", "alt", "alp", "amylase", "ggt", "albumin"],
)

insulin_panel = RequisitionPanel(
    name=INSULIN,
    verbose_name="Insulin",
    abbreviation="INS",
    processing_profile=insulin_processing,
    utest_ids=["ins"],
)

sputum_panel = RequisitionPanel(
    name=SPUTUM,
    verbose_name="Sputum",
    abbreviation="SPM",
    processing_profile=sputum_processing,
    utest_ids=[],
)
