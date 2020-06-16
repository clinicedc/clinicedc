from edc_utils import get_utcnow


GRADING = "grading"
NORMAL = "normal"


def get_references(
    value_references=None,
    gender=None,
    dob=None,
    report_datetime=None,
    units=None,
    **extra_options,
):
    """Returns a list of references for this
    gender, age and units.

    Either ValueReferences or GradeReferences.
    """
    references = []
    report_datetime = report_datetime or get_utcnow()
    for refs in value_references.values():
        for ref in refs:
            non_matching_opts = [
                k for k, v in extra_options.items() if getattr(ref, k) != v
            ]
            if (
                gender in ref.gender
                and ref.units == units
                and ref.age_match(dob, report_datetime)
                and not non_matching_opts
            ):
                references.append(ref)
    return references


class InvalidValueReference(Exception):
    pass


class ValueReferenceNotFound(Exception):
    pass


class ValueReferenceAlreadyAdded(Exception):
    pass


class BoundariesOverlap(Exception):
    pass


class NotEvaluated(Exception):
    pass


class Result:
    def __init__(self, value, description):
        self._value = value
        self.description = description(value=value)

    def __str__(self):
        return self.description


class Normal(Result):
    pass


class Grade(Result):
    def __init__(self, value, grade, description):
        super().__init__(value, description)
        self.grade = grade


class ValueReferenceGroup:
    def __init__(self, name=None):
        self.name = name
        self.normal = {}
        self.grading = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def add_normal(self, normal_reference):
        """Adds a ValueReference to the dictionary of
        normal references.
        """
        self._add(normal_reference, self.normal)

    def add_grading(self, grade_reference):
        """Adds a GradeReference to the dictionary of
        grading references.
        """
        self._add(grade_reference, self.grading)

    def get_normal_description(self, **kwargs):
        """Returns a list of descriptions of the normal references
        for these criteria.
        """
        descriptions = []
        for value_ref in self._get_normal_references(**kwargs):
            descriptions.append(value_ref.description())
        return descriptions

    def get_normal(self, value=None, **kwargs):
        """Returns a Normal instance or None.
        """
        normal = None
        for value_ref in self._get_normal_references(**kwargs):
            if value_ref.in_bounds(value=value, **kwargs):
                if not normal:
                    normal = Normal(value, value_ref.description)
                else:
                    raise BoundariesOverlap(
                        f"Previously got {normal}. "
                        f"Got {value_ref.description(value=value)}. "
                        "Check your definitions."
                    )
        return normal

    def get_grade(self, value=None, **kwargs):
        """Returns a Grade instance or None.
        """
        grade = None
        for grade_ref in self._get_grading_references(**kwargs):
            if grade_ref.in_bounds(value=value, **kwargs):
                if not grade:
                    grade = Grade(value, grade_ref.grade, grade_ref.description)
                else:
                    raise BoundariesOverlap(
                        f"Previously got {grade}. "
                        f"Got {grade_ref.description(value=value)} ",
                        "Check your definitions.",
                    )
        return grade

    def _get_normal_references(self, **kwargs):
        """Returns a list of ValueReference instances or raises.
        """
        references = get_references(value_references=self.normal, **kwargs)
        if not references:
            raise NotEvaluated(
                f"{self.name} value not evaluated. "
                f"No reference range found for {kwargs}. See {repr(self)}."
            )
        return references

    def _get_grading_references(self, **kwargs):
        """Returns a list of GradeReference instances or raises.
        """
        references = get_references(value_references=self.grading, **kwargs)
        if not references:
            raise NotEvaluated(
                f"{self.name} value not graded. "
                f"No reference range found for {kwargs}. See {repr(self)}."
            )
        references.sort(key=lambda x: x.grade, reverse=True)
        return references

    def _add(self, value_reference, value_references):
        if value_reference.name != self.name:
            raise InvalidValueReference(
                "Cannot add to group; name does not match. "
                f"Expected '{self.name}'. Got '{value_reference.name}'. "
                f"See {repr(value_reference)}"
            )
        try:
            if value_reference in value_references[value_reference.gender]:
                raise ValueReferenceAlreadyAdded(
                    f"Value reference {value_reference} has already been added."
                )
        except KeyError:
            value_references[value_reference.gender] = []
        value_references[value_reference.gender].append(value_reference)
