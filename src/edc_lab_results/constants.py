BLOOD_RESULTS_EGFR_ACTION = "abnormal-blood-results-egfr"
BLOOD_RESULTS_FBC_ACTION = "abnormal-blood-results-fbc"
BLOOD_RESULTS_GLU_ACTION = "abnormal-blood-results-glu"
BLOOD_RESULTS_HBA1C_ACTION = "abnormal-blood-results-hba1c"
BLOOD_RESULTS_INSULIN_ACTION = "abnormal-blood-results-ins"
BLOOD_RESULTS_LFT_ACTION = "abnormal-blood-results-lft"
BLOOD_RESULTS_LIPIDS_ACTION = "abnormal-blood-results-lipid"
BLOOD_RESULTS_RFT_ACTION = "abnormal-blood-results-rft"
URINALYSIS_ACTION = "abnormal-urinalysis"

PENDING = "pending"
IMPORTED = "imported"
ERROR = "error"

# Result.requisition_match_category — outcome/reason of automatic
# requisition matching in LabResultImporter.link_requisitions().
LINKED = "linked"
AMBIGUOUS_MULTI_PANEL = "ambiguous_multi_panel"
AMBIGUOUS_SAME_PANEL = "ambiguous_same_panel"
NO_MATCH = "no_match"
# utest_id is not defined on any registered panel (e.g. extra lab analytes
# the EDC does not track). Cannot be matched to a requisition by panel.
NO_PANEL_FOR_UTEST_ID = "no_panel_for_utest_id"
# investigation has no EDC utest_id mapping at all (result.utest_id is blank).
NO_UTEST_ID = "no_utest_id"
SUBJECT_NOT_FOUND = "subject_not_found"
# name_id does not resolve AND its identifier is not valid for this deployment
# (wrong protocol, unregistered site, or unrecognizable) -- another protocol's
# data flowing through a shared lab inbox, or junk. Not actionable here.
OUT_OF_SCOPE = "out_of_scope"

# classify_identifier() reason codes (stored in requisition_match_comment).
REASON_VALID_SUBJECT = "valid_subject"
REASON_BAD_CHECK_DIGIT = "bad_check_digit"
REASON_UNREGISTERED_SITE = "unregistered_site"
# matches the screening pattern and IS a known SubjectScreening.
REASON_VALID_SCREENING = "valid_screening"
# matches the screening pattern but is NOT in SubjectScreening -> a site/lab
# typo of a screening identifier (reissue-able).
REASON_INVALID_SCREENING = "invalid_screening"
REASON_FOREIGN = "foreign"

# Categories that need human action, surfaced in the review worklist.
# Deliberately excludes LINKED (done) and NO_PANEL_FOR_UTEST_ID / NO_UTEST_ID
# (untracked analytes / unmapped investigations, not actionable per-result).
REVIEW_CATEGORIES = (
    SUBJECT_NOT_FOUND,
    NO_MATCH,
    AMBIGUOUS_MULTI_PANEL,
    AMBIGUOUS_SAME_PANEL,
)
