from edc_reportable.exceptions import NotEvaluated
from edc_reportable.utils import get_reference_range_collection

__all__ = ["get_summary"]


def get_summary(obj) -> tuple[list[str], list[str], list[str]]:
    """Returns a list of graded or abnormal values given a
    BloodResultsModel instance.
    """
    opts = obj.get_summary_options()
    reportable = []
    abnormal = []
    errors = []
    for field_name in [f.name for f in obj._meta.get_fields()]:
        try:
            utest_id, _ = field_name.split("_value")
        except ValueError:
            utest_id = field_name
        reference_range_collection = get_reference_range_collection(obj)
        units = getattr(obj, f"{utest_id}_units", None)
        value = getattr(obj, field_name)
        if units and value:
            opts.update(units=units, label=utest_id)
            try:
                grading_data, grading_eval_phrase = reference_range_collection.get_grade(
                    value, **opts
                )
            except NotEvaluated as e:
                errors.append(f"{e}.")
                grading_data = None
                grading_eval_phrase = None
            if (
                grading_data
                and grading_data.grade
                in reference_range_collection.reportable_grades(utest_id)
            ):
                setattr(obj, f"{utest_id}_grade", grading_data.grade)
                setattr(obj, f"{utest_id}_grade_description", grading_data.description)
                reportable.append(f"{grading_eval_phrase}")
            else:
                try:
                    is_normal, normal_data = reference_range_collection.is_normal(
                        value, **opts
                    )
                except NotEvaluated as e:
                    errors.append(f"{e}.")
                else:
                    if is_normal is False:
                        abnormal.append(
                            f"{normal_data.label}: {value} {units} "
                            f"{normal_data.phrase} Abnormal"
                        )
    return reportable, abnormal, errors
