from .age_evaluator import AgeEvaluator
from .gender_evaluator import GenderEvaluator


class EligibilityError(Exception):
    pass


class Eligibility:

    """Eligible if all criteria evaluate True.

    Any key in `additional_criteria` has value True if eligible.
    """

    # default to M or F
    gender_evaluator_cls = GenderEvaluator

    # default to eligible if >=18
    age_evaluator = AgeEvaluator(age_lower=18, age_lower_inclusive=True)

    custom_reasons_dict: dict = {}

    def __init__(
        self,
        age: int = None,
        gender: str = None,
        pregnant: bool = None,
        breast_feeding: bool = None,
        **additional_criteria,
    ) -> None:
        self.criteria = dict(**additional_criteria)
        if len(self.criteria) == 0:
            raise EligibilityError("No criteria provided.")

        self.gender_evaluator = self.gender_evaluator_cls(
            gender=gender, pregnant=pregnant, breast_feeding=breast_feeding
        )
        self.criteria.update(age=self.age_evaluator.eligible(age))
        self.criteria.update(gender=self.gender_evaluator.eligible)

        # hook for custom checks
        self.criteria.update(**self.extra_eligibility_criteria)

        # eligible if all criteria are True
        self.eligible = all([v for v in self.criteria.values()])

        if self.eligible:
            self.reasons_ineligible = None
        else:
            self.reasons_ineligible = {k: v for k, v in self.criteria.items() if not v}
            for k, v in self.criteria.items():
                if not v:
                    if k in self.get_custom_reasons_dict():
                        self.reasons_ineligible.update(
                            {k: self.get_custom_reasons_dict().get(k)}
                        )
                    elif k not in ["age", "gender"]:
                        self.reasons_ineligible.update({k: k})
            if not self.age_evaluator.eligible(age):
                self.reasons_ineligible.update(age=self.age_evaluator.reasons_ineligible)
            if not self.gender_evaluator.eligible:
                self.reasons_ineligible.update(
                    gender=f"{' and '.join(self.gender_evaluator.reasons_ineligible)}."
                )

    def __str__(self):
        return self.eligible

    @property
    def extra_eligibility_criteria(self) -> dict:
        return {}

    def get_custom_reasons_dict(self) -> dict:
        """Returns a dictionary of custom reasons for named criteria."""
        for k in self.custom_reasons_dict:
            if k in self.custom_reasons_dict and k not in self.criteria:
                raise EligibilityError(
                    f"Custom reasons refer to invalid named criteria, Got '{k}'. "
                    f"Expected one of {list(self.criteria)}. "
                    f"See {repr(self)}."
                )
        return self.custom_reasons_dict
