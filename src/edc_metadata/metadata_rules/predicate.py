from __future__ import annotations

from typing import Any

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class PredicateError(Exception):
    pass


class NoValueError(Exception):
    pass


class BasePredicate:
    @staticmethod
    def get_value(attr: str = None, source_model: str | None = None, **kwargs) -> Any:
        """Returns a value by checking for the attr on each arg.

        Each arg in args may be a model instance, queryset, or None.

        If not found, does a lookup on the source_model.
        """
        found: bool = False
        value: Any = None
        for v in kwargs.values():
            try:
                value = getattr(v, attr)
            except AttributeError:
                continue
            else:
                found = True
                break
        if not found:
            visit = kwargs.get("visit")
            try:
                obj = django_apps.get_model(source_model).objects.get(
                    subject_visit__subject_identifier=visit.subject_identifier,
                    subject_visit__visit_schedule_name=visit.visit_schedule_name,
                    subject_visit__schedule_name=visit.schedule_name,
                    subject_visit__visit_code=visit.visit_code,
                    subject_visit__visit_code_sequence=visit.visit_code_sequence,
                    subject_visit__site=visit.site,
                )
            except ObjectDoesNotExist:
                value = None
            else:
                value = getattr(obj, attr)
        return value


class P(BasePredicate):

    """
    Simple predicate class.

    For example:

        predicate = P('gender', 'eq', 'MALE')
        predicate = P('referral_datetime', 'is not', None)
        predicate = P('age', '<=', 64)
    """

    funcs = {
        "is": lambda x, y: True if x is y else False,
        "is not": lambda x, y: True if x is not y else False,
        "gt": lambda x, y: True if x > y else False,
        ">": lambda x, y: True if x > y else False,
        "gte": lambda x, y: True if x >= y else False,
        ">=": lambda x, y: True if x >= y else False,
        "lt": lambda x, y: True if x < y else False,
        "<": lambda x, y: True if x < y else False,
        "lte": lambda x, y: True if x <= y else False,
        "<=": lambda x, y: True if x <= y else False,
        "eq": lambda x, y: True if x == y else False,
        "equals": lambda x, y: True if x == y else False,
        "==": lambda x, y: True if x == y else False,
        "neq": lambda x, y: True if x != y else False,
        "!=": lambda x, y: True if x != y else False,
        "in": lambda x, y: True if x in y else False,
    }

    def __init__(self, attr: str, operator: str, expected_value: list | str) -> None:
        self.attr = attr
        self.expected_value = expected_value
        self.func = self.funcs.get(operator)
        if not self.func:
            raise PredicateError(f"Invalid operator. Got {operator}.")
        self.operator = operator

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.attr}, {self.operator}, "
            f"{self.expected_value})"
        )

    def __call__(self, **kwargs) -> bool:
        value = self.get_value(attr=self.attr, **kwargs)
        return self.func(value, self.expected_value)


class PF(BasePredicate):
    """
    Predicate with a lambda function.

    predicate = PF('age', lambda x: True if x >= 18 and x <= 64 else False)

    if lamda is anything more complicated just pass a func directly to the predicate attr:

        def my_func(visit, registered_subject, source_obj, source_qs):
            if source_obj.married and registered_subject.gender == FEMALE:
                return True
            return False

        class MyRuleGroup(RuleGroup):

            my_rule = Rule(
                ...
                predicate = my_func
                ...

    """

    def __init__(self, *attrs, func: callable = None) -> None:
        self.attrs = attrs
        self.func = func

    def __call__(self, **kwargs) -> Any:
        values = []
        for attr in self.attrs:
            values.append(self.get_value(attr=attr, **kwargs))
        return self.func(*values)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.attrs}, {self.func})"
