from datetime import date, datetime

from edc_utils import get_utcnow

from .grade_reference import GradeReference
from .normal_reference import NormalReference


def get_reference_range_collection_name(obj) -> str:
    """Returns the reference range name.

    Expects either a model with requisition attr or a requisition.
    """
    try:
        return obj.requisition.panel_object.reference_range_collection_name
    except AttributeError:
        return obj.panel_object.reference_range_collection_name


def get_references_by_criteria(
    value_references: dict[str, list[NormalReference | GradeReference]] = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    units: str = None,
    **extra_options,
):
    """Returns a list of references for this gender, age and units.

    Either ValueReferences or GradeReferences.
    """
    references = []
    report_datetime = report_datetime or get_utcnow()
    for refs in value_references.values():
        for ref in refs:
            non_matching_opts = [k for k, v in extra_options.items() if getattr(ref, k) != v]
            if (
                gender in ref.gender
                and ref.units == units
                and ref.age_match(dob, report_datetime)
                and not non_matching_opts
            ):
                references.append(ref)
    return references
