from edc_lab import RequisitionPanel

from .processing_profiles import (
    blood_glucose_processing,
    fbc_processing,
    hba1c_processing,
    insulin_processing,
    lft_processing,
    lipids_processing,
    poc_processing,
    rft_processing,
    sputum_processing,
)

hba1c_panel = RequisitionPanel(
    name="hba1c",
    verbose_name="HbA1c (Venous)",
    processing_profile=hba1c_processing,
    abbreviation="HBA1C",
    utest_ids=[("hba1c", "HbA1c")],
)


hba1c_poc_panel = RequisitionPanel(
    name="hba1c_poc",
    verbose_name="HbA1c (POC)",
    abbreviation="HBA1C_POC",
    processing_profile=poc_processing,
    utest_ids=[("hba1c", "HbA1c")],
)


fbc_panel = RequisitionPanel(
    name="fbc",
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
    name="blood_glucose",
    verbose_name="Blood Glucose (Venous)",
    abbreviation="BGL",
    processing_profile=blood_glucose_processing,
    utest_ids=[("glucose", "Glucose")],
)

blood_glucose_poc_panel = RequisitionPanel(
    name="blood_glucose_poc",
    verbose_name="Blood Glucose (POC)",
    abbreviation="BGL-POC",
    processing_profile=poc_processing,
    utest_ids=[("glucose", "Glucose")],
)


rft_panel = RequisitionPanel(
    name="chemistry_rft",
    verbose_name="Chemistry: Renal Function Tests",
    abbreviation="RFT",
    processing_profile=rft_processing,
    utest_ids=["urea", "creatinine", "uric_acid", "egfr"],
)

lipids_panel = RequisitionPanel(
    name="chemistry_lipids",
    verbose_name="Chemistry: Lipids",
    abbreviation="LIPIDS",
    processing_profile=lipids_processing,
    utest_ids=["ldl", "hdl", "trig", "chol"],
)

lft_panel = RequisitionPanel(
    name="chemistry_lft",
    verbose_name="Chemistry: Liver Function Tests",
    abbreviation="LFT",
    processing_profile=lft_processing,
    utest_ids=["ast", "alt", "alp", "amylase", "ggt", "albumin"],
)

insulin_panel = RequisitionPanel(
    name="insulin",
    verbose_name="Insulin",
    abbreviation="INS",
    processing_profile=insulin_processing,
    utest_ids=["ins"],
)

sputum_panel = RequisitionPanel(
    name="sputum",
    verbose_name="Sputum",
    abbreviation="SPM",
    processing_profile=sputum_processing,
    utest_ids=[],
)
