from django.utils.translation import gettext_lazy as _

from .constants import (
    ABNORMAL,
    ABSENT,
    AFTERNOON,
    ALIVE,
    ALWAYS,
    ANYTIME,
    AWAITING_RESULTS,
    COMPLETE,
    DEAD,
    DECLINED,
    DONT_KNOW,
    DWTA,
    EVENING,
    FALSE,
    FASTING,
    FEMALE,
    FORMER_SMOKER,
    HIGH,
    INCOMPLETE,
    IND,
    LOW,
    MALE,
    MORNING,
    NAIVE,
    NEG,
    NEVER,
    NO,
    NON_FASTING,
    NONSMOKER,
    NORMAL,
    NOT_APPLICABLE,
    NOT_DONE,
    NOT_ESTIMATED,
    NOT_EVALUATED,
    NOT_EXAMINED,
    NOT_RECORDED,
    NOT_REQUIRED,
    NOT_SURE,
    OMANG,
    OTHER,
    PENDING,
    POS,
    PRESENT,
    PURPOSIVELY_SELECTED,
    QUESTION_RETIRED,
    RANDOM_SAMPLING,
    RARELY,
    REFUSED,
    SMOKER,
    SOMETIMES,
    TBD,
    TRUE,
    UNKNOWN,
    VERY_OFTEN,
    WEEKDAYS,
    WEEKENDS,
    YES,
)

ACU_EST = (
    ("Acute", _("Acute")),
    ("Established", _("Established")),
)

ACU_EST_NEG = (
    ("Acute", _("Acute")),
    ("Established", _("Established")),
    ("Negative", _("Negative")),
)

ALIVE_DEAD = (
    (ALIVE, _("Alive")),
    (DEAD, _("Dead")),
)

ALIVE_DEAD_UNKNOWN = (
    (ALIVE, _("Alive")),
    (DEAD, _("Deceased")),
    (UNKNOWN, _("Unknown")),
)

ALIVE_DEAD_UNKNOWN_NA = (
    (ALIVE, _("Alive")),
    (DEAD, _("Deceased")),
    (UNKNOWN, _("Unknown")),
    (NOT_APPLICABLE, _("Not applicable")),
)

ALIVE_DEAD_UNKNOWN_NA_MISSED = (
    (ALIVE, _("Alive")),
    (DEAD, _("Deceased")),
    (UNKNOWN, _("Unknown")),
    (NOT_APPLICABLE, _("Not applicable (if missed)")),
)


ART_STATUS = (
    ("ON", _("Yes, on ART")),
    ("STOPPED", _("No, stopped ART")),
    (NAIVE, _("No, have never taken ART")),
)

ART_STATUS_UNKNOWN = (
    ("ON", _("ON ART")),
    ("STOPPED", _("Stopped")),
    (NAIVE, _("Naive")),
    (UNKNOWN, _("Unknown")),
)

ART_STATUS_CONFIRM = (
    ("OPD", _("%(num)s Show OPD/IDCC card" % {"num": "1."})),
    ("Pills", _("%(num)s Show pills" % {"num": "2."})),
    ("Pic", _("%(num)s Identify pictorial" % {"num": "3."})),
)

ARV_DRUG_LIST = (
    ("Nevirapine", "NVP"),
    ("Kaletra", "KAL"),
    ("Aluvia", "ALU"),
    ("Truvada", "TRV"),
    ("Tenoforvir", "TDF"),
    ("Zidovudine", "AZT"),
    ("Lamivudine", "3TC"),
    ("Efavirenz", "EFV"),
    ("Didanosine", "DDI"),
    ("Stavudine", "D4T"),
    ("Nelfinavir", "NFV"),
    ("Abacavir", "ABC"),
    ("Combivir", "CBV"),
    ("Ritonavir", "RTV"),
    ("Trizivir", "TZV"),
    ("Raltegravir", "RAL"),
    ("Saquinavir,soft gel capsule", "FOR"),
    ("Saquinavir,hard capsule", "INV"),
    ("Kaletra or Aluvia", _("KAL or ALU")),
    ("Atripla", "ATR"),
    ("HAART,unknown", _("HAART,unknown")),
)

ARV_MODIFICATION_REASON = (
    ("Initial dose", _("Initial dose")),
    ("Never started", _("Never started")),
    ("Toxicity decreased_resolved", _("Toxicity decreased/resolved")),
    ("Completed PMTCT intervention", _("Completed PMTCT intervention")),
    ("Completed postpartum tail", _('Completed post-partum "tail"')),
    ("Scheduled dose increase", _("Scheduled dose increase")),
    (
        "Confirmed infant HIV infection, ending study drug",
        _("Confirmed infant HIV infection, ending study drug"),
    ),
    (
        "completed protocol",
        _("Completion of protocol-required period of study treatment"),
    ),
    ("HAART not available", _("HAART not available")),
    ("Anemia", _("Anemia")),
    ("Bleeding", _("Bleeding")),
    ("CNS symptoms", _("CNS symptoms (sleep, psych, etc)")),
    ("Diarrhea", _("Diarrhea")),
    ("Fatigue", _("Fatigue")),
    ("Headache", _("Headache")),
    ("Hepatotoxicity", _("Hepatotoxicity")),
    ("Nausea", _("Nausea")),
    ("Neutropenia", _("Neutropenia")),
    ("Thrombocytopenia", _("Thrombocytopenia")),
    ("Vomiting", _("Vomiting")),
    ("Rash", _("Rash")),
    ("Rash resolved", _("Rash resolved")),
    ("Neuropathy", _("Neuropathy")),
    ("Hypersensitivity_allergic reaction", _("Hypersensitivity / allergic reaction")),
    ("Pancreatitis", _("Pancreatitis")),
    ("Lactic Acidiosis", _("Lactic Acidiosis")),
    ("Pancytopenia", _("Pancytopenia")),
    ("Virologic failure", _("Virologic failure")),
    ("Immunologic failure", _("Immunologic failure(CD4)")),
    ("Clinical failure", _("Clinical failure")),
    ("Clinician request", _("Clinician request, other reason (including convenience)")),
    ("Subject request", _("Subject request, other reason (including convenience)")),
    ("Non-adherence with clinic visits", _("Non-adherence with clinic visits")),
    ("Non-adherence with ARVs", _("Non-adherence with ARVs")),
    ("Death", _("Death")),
    (OTHER, _("Other")),
)


ARV_STATUS = (
    ("no_mod", _("1. No modifications made to existing HAART treatment")),
    (
        "start",
        (
            _(
                "2. Started antriretroviral treatment since last "
                "attended scheduled visit(including today)"
            )
        ),
    ),
    (
        "discontinued",
        _(
            "3. Permanently discontinued antiretroviral treatment at "
            "or before last study visit"
        ),
    ),
    (
        "modified",
        _(
            "4. Change in at least one antiretroviral medication since last "
            "attended scheduled visit (including today)(dose modification, "
            "permanent discontinuation, temporary hold, resumption / initiation "
            "after temporary hold)"
        ),
    ),
)

ARV_STATUS_WITH_NEVER = (
    (
        "no_mod",
        _("1. No modifications made since the last attended scheduled visit or today"),
    ),
    (
        "start",
        _("2. Starting today or has started since last attended scheduled visit"),
    ),
    (
        "discontinued",
        _("3. Permanently discontinued at or before the last attended scheduled visit"),
    ),
    ("never started", _("4. Never started")),
    (
        "modified",
        _(
            "5. Change in at least one medication since the "
            "last attended scheduled visit or today"
        ),
    ),
    (NOT_APPLICABLE, _("Not applicable")),
)

CONFIRMED_SUSPECTED = (
    ("CONFIRMED", _("Confirmed")),
    ("SUSPECTED", _("Suspected")),
)

COUNTRY = (
    ("botswana", _("Botswana")),
    ("zimbabwe", _("Zimbabwe")),
    ("rsa", _("South Africa")),
    ("zambia", _("Zambia")),
    ("namibia", _("Namibia")),
    ("nigeria", _("Nigeria")),
    ("china", _("China")),
    ("india", _("India")),
    ("OTHER", _("Other")),
)

DAYS_OF_WEEK = (
    ("Monday", _("Monday")),
    ("Tuesday", _("Tuesday")),
    ("Wednesday", _("Wednesday")),
    ("Thursday", _("Thursday")),
    ("Friday", _("Friday")),
    ("Saturday", _("Saturday")),
    ("Sunday", _("Sunday")),
    ("AnyDay", _("Any day")),
)

DAYS_OF_WEEK_ONLY = (
    ("Monday", _("Monday")),
    ("Tuesday", _("Tuesday")),
    ("Wednesday", _("Wednesday")),
    ("Thursday", _("Thursday")),
    ("Friday", _("Friday")),
    ("Saturday", _("Saturday")),
    ("Sunday", _("Sunday")),
)

DATE_ESTIMATED_NA = (
    (NOT_APPLICABLE, _("Not applicable")),
    (NOT_ESTIMATED, _("No")),
    ("D", _("Yes, estimated the Day")),
    ("MD", _("Yes, estimated Month and Day")),
    ("YMD", _("Yes, estimated Year, Month and Day")),
)

DATE_ESTIMATED = (
    ("-", _("No")),
    ("D", _("Yes, estimated the Day")),
    ("MD", _("Yes, estimated Month and Day")),
    ("YMD", _("Yes, estimated Year, Month and Day")),
)

DEATH_RELATIONSIP_TO_STUDY = (
    ("Definitely not related", _("Definitely not related")),
    ("Probably not related", _("Probably not related")),
    ("Possible related", _("Possible related")),
    ("Probably related", _("Probably related")),
    ("Definitely related", _("Definitely related")),
)

DOCUMENT_STATUS = (
    (INCOMPLETE, _("Incomplete (some data pending)")),
    (COMPLETE, _("Complete")),
)

DOSE_STATUS = (
    ("New", _("New")),
    ("Permanently discontinued", _("Permanently discontinued")),
    ("Temporarily held", _("Temporarily held")),
    ("Dose modified", _("Dose modified")),
    ("Resumed", _("Resumed")),
    ("Not initiated", _("Not initiated")),
)

FASTING_CHOICES = ((FASTING, _("Fasting")), (NON_FASTING, _("Non-fasting")))

FEEDING = (
    ("BF", _("Breast feed")),
    ("FF", _("Formula feed")),
)

GENDER = ((MALE, _("Male")), (FEMALE, _("Female")))

GENDER_NA = (
    (MALE, _("Male")),
    (FEMALE, _("Female")),
    (NOT_APPLICABLE, _("Not applicable")),
)

GENDER_UNDETERMINED = (
    (MALE, _("Male")),
    (FEMALE, _("Female")),
    ("U", _("Undetermined")),
)

GRADING_SCALE = (
    (1, _("Grade 1")),
    (2, _("Grade 2")),
    (3, _("Grade 3")),
    (4, _("Grade 4")),
    (5, _("Grade 5")),
)

GRADING_SCALE_WITH_NOT_GRADED = (
    (0, _("Not graded")),
    (1, _("Grade 1")),
    (2, _("Grade 2")),
    (3, _("Grade 3")),
    (4, _("Grade 4")),
    (5, _("Grade 5")),
)

GRADING_SCALE_234 = (
    (2, _("Grade 2")),
    (3, _("Grade 3")),
    (4, _("Grade 4")),
)


GRADING_SCALE_34 = (
    (3, _("Grade 3")),
    (4, _("Grade 4")),
)

HIGH_LOW_NA = (
    (HIGH, _("High")),
    (LOW, _("Low")),
    (NOT_APPLICABLE, _("Not applicable")),
)

HIV_RESULT = (
    (POS, _("HIV Positive (Reactive)")),
    (NEG, _("HIV Negative (Non-reactive)")),
    (IND, _("Indeterminate")),
    (DECLINED, _("Participant declined testing")),
    (
        "Not performed",
        _("Test could not be performed (e.g. supply outage, technical problem)"),
    ),
)

# do not change without inspecting implication to check_omang_field() in utils.py
IDENTITY_TYPE = (
    (OMANG, _("Omang")),
    ("DRIVERS", _("Driver's License")),
    ("PASSPORT", _("Passport")),
    ("OMANG_RCPT", _("Omang Receipt")),
    (OTHER, _("Other")),
)

LIKERT_FREQUENCY = (
    (ALWAYS, _("Always")),
    (VERY_OFTEN, _("Very Often")),
    (SOMETIMES, _("Sometimes")),
    (RARELY, _("Rarely")),
    (NEVER, _("Never")),
)

MARITAL_STATUS = (
    ("never_married", _("Never married")),
    ("married", _("Currently married")),
    ("separated", _("Separated")),
    ("divorced", _("Divorced")),
    ("widowed", _("Widow / Spinster")),
)

NORMAL_ABNORMAL = (
    (NORMAL, _("Normal")),
    (ABNORMAL, _("Abnormal")),
)

NORMAL_ABNORMAL_NOEXAM = (
    (NORMAL, _("Normal")),
    (ABNORMAL, _("Abnormal")),
    ("NO_EXAM", _("No exam performed")),
)

NORMAL_ABNORMAL_NOTEVALUATED = (
    (NORMAL, _("Normal")),
    (ABNORMAL, _("Abnormal")),
    ("NOT_EVAL", _("Not evaluated")),
)

POS_NEG = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (IND, _("Indeterminate")),
)

POS_NEG_REFUSED = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (IND, _("Indeterminate")),
    ("REF", _("Refused to disclose")),
)

POS_NEG_IND_NA = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (IND, _("Indeterminate")),
    (NOT_APPLICABLE, _("Not applicable")),
)

POS_NEG_ANY = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    ("ANY", _("Any")),
)

POS_NEG_NA = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (NOT_APPLICABLE, _("Not applicable")),
)

POS_NEG_ONLY = ((POS, _("Positive")), (NEG, _("Negative")))

POS_NEG_UNKNOWN = ((POS, _("Positive")), (NEG, _("Negative")), (UNKNOWN, _("Unknown")))

POS_NEG_IND_UNKNOWN = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (IND, _("Indeterminate")),
    (UNKNOWN, _("Unknown")),
)

POS_NEG_ACU = (
    ("Positive", _("Positive")),
    ("Negative", _("Negative")),
    ("Possible Acute", _("Possible acute")),
    ("Indeterminate", _("Indeterminate")),
)

POS_NEG_NOTESTED = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (NEVER, _("Never tested for HIV")),
)

POS_NEG_NOT_DONE = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (NOT_DONE, _("Not done")),
)

POS_NEG_NOT_DONE_NA = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (NOT_DONE, _("Not done")),
    (NOT_APPLICABLE, _("Not applicable")),
)

POS_NEG_NOT_DONE_NOT_EVALUATED = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (NOT_DONE, _("Not done")),
    (NOT_EVALUATED, _("Not evaluated")),
)

POS_NEG_UNTESTED_REFUSAL = (
    (POS, _("Positive")),
    (NEG, _("Negative")),
    (IND, _("Indeterminate")),
    (NEVER, _("Never tested for HIV")),
    (UNKNOWN, _("Unknown")),
    (DWTA, _("Don't want to answer")),
)

PREG_YES_NO_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_APPLICABLE, _("Not Applicable: e.g. male or post-menopausal")),
)

PRESENT_ABSENT = (
    (PRESENT, _("Present")),
    (ABSENT, _("Absent")),
)

PRESENT_ABSENT_NA = (
    (PRESENT, _("Present")),
    (ABSENT, _("Absent")),
    (NOT_APPLICABLE, _("Not Applicable")),
)

REFUSAL_STATUS = (
    (REFUSED, _("Refused")),
    ("NOT_REFUSED", _("No longer refusing")),
)

SELECTION_METHOD = (
    (RANDOM_SAMPLING, _("Random sampling")),
    (PURPOSIVELY_SELECTED, _("Purposively selected")),
)

SEVERITY_LEVEL = (
    ("mild", _("Mild")),
    ("moderate", _("Moderate")),
    ("severe", _("Severe")),
)

SEXUAL_DEBUT = (
    ("<=14", _("14 or under")),
    ("15-17", _("15 - 17")),
    (">=18", _("18 or above")),
)

SMOKER_STATUS_SIMPLE = (
    (SMOKER, _("Currently smoke")),
    (FORMER_SMOKER, _("Used to smoke but stopped")),
    (NONSMOKER, _("Never smoked")),
)

SMOKER_STATUS = (
    (SMOKER, _("Currently smoke")),
    (FORMER_SMOKER, _("Used to smoke but stopped")),
    (NONSMOKER, _("Never smoked")),
    (NOT_RECORDED, _("Not recorded")),
)


TIME_OF_WEEK = (
    (WEEKDAYS, _("Weekdays")),
    (WEEKENDS, _("Weekends")),
    (ANYTIME, _("Anytime")),
)

TIME_OF_DAY = (
    (MORNING, _("Morning")),
    (AFTERNOON, _("Afternoon")),
    (EVENING, _("Evening")),
    (ANYTIME, _("Anytime")),
)

TIME_UNITS = (
    ("TODAY", _("Today")),
    ("DAYS", _("Days")),
    ("WEEKS", _("Weeks")),
    ("MONTHS", _("Months")),
    ("YEARS", _("Years")),
)

TRUE_FALSE_DONT_KNOW = (
    (TRUE, _("True")),
    (FALSE, _("False")),
    (DONT_KNOW, _("Don't know")),
)


URINALYSIS = (
    ("NAD", "NAD"),
    ("Sugar Neg", _("Sugar Neg")),
    ("Sugar +", _("Sugar +")),
    ("Sugar ++", _("Sugar ++")),
    ("Sugar +++", _("Sugar +++")),
    ("Blood", _("Blood")),
    ("Protein", _("Protein")),
    ("Cells", _("Cells")),
)

YES_NO = ((YES, _(YES)), (NO, _(NO)))

YESDEFAULT_NO = ((YES, _("Yes (default)")), (NO, _(NO)))

YES_NO_AWAITING_RESULTS = (
    (YES, _(YES)),
    (NO, _(NO)),
    (AWAITING_RESULTS, _("Awaiting results")),
)

YES_NO_NOT_DONE_AWAITING_RESULTS = (
    (YES, _(YES)),
    (NO, _(NO)),
    (AWAITING_RESULTS, _("Awaiting results")),
    (NOT_DONE, _("Not done")),
)

YES_NO_NOT_DONE_AWAITING_RESULTS_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (AWAITING_RESULTS, _("Awaiting results")),
    (NOT_DONE, _("Not done")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_DECLINED = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DECLINED, _("Yes, but subject declined copy")),
)

YES_NO_OPTIONAL = (
    (YES, _(YES)),
    (NO, _(NO)),
    ("Optional", _("Optional")),
)

YES_NO_REFUSED = (
    (YES, _(YES)),
    (NO, _(NO)),
    (REFUSED, _("Refused to answer")),
)

YES_NO_DWTA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DWTA, _("Don't want to answer")),
)

YES_NO_NA_SPECIFY = (
    (YES, _("Yes, (Specify below)")),
    (NO, _(NO)),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_PENDING = (
    (YES, _(YES)),
    (NO, _(NO)),
    (PENDING, _("Pending")),
)

YES_NO_PENDING_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (PENDING, _("Pending")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_PENDING_NA_GLUCOSE_SCREENING = (
    (PENDING, _("Pending (scheduled for 3 days from first)")),
    (YES, _(YES)),
    (NOT_APPLICABLE, _("Not applicable")),
)


YES_NO_NA_DWTA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DWTA, _("Don't want to answer")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_NOT_EVALUATED = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_EVALUATED, _("Not evaluated")),
)

YES_NO_NOT_EVALUATED_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_APPLICABLE, _("Not applicable")),
    (NOT_EVALUATED, _("Not evaluated")),
)

YES_NO_NOT_EXAMINED = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_EXAMINED, _("Not examined")),
)


YES_NO_NOT_DONE = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_DONE, _("Not done")),
)

YES_NO_UNKNOWN = (
    (YES, _(YES)),
    (NO, _(NO)),
    (UNKNOWN, _("Unknown")),
)

YES_NO_NA_DWTA_DNK = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DWTA, _("Don't want to answer")),
    ("cant_remember", _("Cannot remember")),
)

YES_NO_TBD = (
    (YES, _(YES)),
    (NO, _(NO)),
    (TBD, _("To be determined")),
)

YES_NO_UNKNOWN_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (UNKNOWN, _("Unknown")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_UNKNOWN_NA_MISSED = (
    (YES, _(YES)),
    (NO, _(NO)),
    (UNKNOWN, _("Unknown")),
    (NOT_APPLICABLE, _("Not applicable (if missed)")),
)

YES_NO_UNSURE = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_SURE, _("Not sure")),
)

YES_NO_UNSURE_DWTA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_SURE, _("Not sure")),
    (DWTA, _("Don't want to answer")),
)

YES_NO_UNSURE_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (NOT_SURE, _("Not sure")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_DONT_KNOW = (
    (YES, _(YES)),
    (NO, _(NO)),
    ("Dont_know", _("Don't know")),
)

YES_NO_DONT_KNOW_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DONT_KNOW, _("Don't know")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_DONT_KNOW_DWTA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DONT_KNOW, _("Don't know")),
    (DWTA, _("Don't want to answer")),
)

YES_NO_DONT_KNOW_DWTA_NA = (
    (YES, _(YES)),
    (NO, _(NO)),
    (DONT_KNOW, _("Don't know")),
    (DWTA, _("Don't want to answer")),
    (NOT_APPLICABLE, _("Not applicable")),
)

YES_NO_DOESNT_WORK = (
    (YES, _(YES)),
    (NO, _(NO)),
    ("Doesnt_work", _("Doesn't work")),
)

YES_NO_NOT_REQUIRED = ((YES, _(YES)), (NO, _(NO)), (NOT_REQUIRED, _("Not required")))

YES_NO_RETIRED = (
    (YES, _(YES)),
    (NO, _(NO)),
    (QUESTION_RETIRED, "Question retired"),
)

WHYNOPARTICIPATE_CHOICE = (
    ("I don't have time", _("I don't have time")),
    ("I don't want to answer the questions", _("I don't want to answer the questions")),
    ("I don't want to have the blood drawn", _("I don't want to have the blood drawn")),
    (
        "I am afraid my information will not be private",
        _("I am afraid my information will not be private"),
    ),
    ("Fear of needles", _("Fear of needles")),
    ("Illiterate does not want a witness", _("Illiterate does not want a witness")),
    ("I don't want to take part", _("I don't want to take part")),
    (
        "I haven't had a chance to think about it",
        _("I haven't had a chance to think about it"),
    ),
    (
        "Have a newly born baby, not permitted",
        _("Have a newly born baby, not permitted"),
    ),
    ("The appointment was not honoured", _("The appointment was not honoured")),
    ("not_sure", _("I'm not sure")),
    ("OTHER", _("Other, specify:")),
    ("not_answering", _("Don't want to answer")),
)
