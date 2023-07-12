from __future__ import annotations

from typing import Any, Optional, Union

from edc_reference.reference import ReferenceGetterError, ReferenceObjectDoesNotExist


class PredicateError(Exception):
    pass


class NoValueError(Exception):
    pass


class BasePredicate:
    def get_value(
        self,
        attr: str = None,
        source_model: str | None = None,
        reference_getter_cls: Optional[Any] = None,
        **kwargs,
    ) -> Any:
        """Returns a value by checking for the attr on each arg.

        Each arg in args may be a model instance, queryset, or None.

        A NoValueError is raised if attr is not found on any "instance".
        in kwargs.
        """
        found_on_instance: Any = None
        for instance in kwargs.values():
            try:
                getattr(instance, attr)
            except AttributeError:
                pass
            else:
                found_on_instance = instance
                break
        if found_on_instance:
            value = getattr(found_on_instance, attr)
        else:
            opts = dict(
                field_name=attr, name=source_model, **self.opts_from_visit(kwargs.get("visit"))
            )
            try:
                reference = reference_getter_cls(**opts)
            except (ReferenceGetterError, ReferenceObjectDoesNotExist) as e:
                raise NoValueError(f"No value found for {attr}. Given {kwargs}. Got {e}.")
            else:
                if reference.has_value:
                    value = getattr(reference, attr)
                else:
                    raise NoValueError(f"No value found for {attr}. Given {kwargs}")
        return value

    @staticmethod
    def opts_from_visit(visit: Any) -> dict:
        """Returns a dict of values from the visit model instance"""
        try:
            opts = dict(
                subject_identifier=visit.subject_identifier,
                report_datetime=visit.report_datetime,
                visit_schedule_name=visit.visit_schedule_name,
                schedule_name=visit.schedule_name,
                visit_code=visit.visit_code,
                visit_code_sequence=visit.visit_code_sequence,
                timepoint=visit.timepoint,
                site=visit.site,
            )
        except AttributeError as e:
            raise PredicateError(f"Invalid visit model or None. Got {e}")
        return opts


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

    def __init__(self, attr: str, operator: str, expected_value: Union[list, str]) -> None:
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
