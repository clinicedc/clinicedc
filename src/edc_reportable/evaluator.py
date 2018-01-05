import re


class InvalidUnits(Exception):
    pass


class InvalidLowerBound(Exception):
    pass


class InvalidUpperBound(Exception):
    pass


class InvalidCombination(Exception):
    pass


class ValueBoundryError(Exception):
    pass


class Evaluator:
    def __init__(self, name=None, lower=None, upper=None, units=None,
                 lower_inclusive=None, upper_inclusive=None, **kwargs):
        self.name = name
        if lower and not re.match('\d+', str(lower)):
            raise InvalidLowerBound(f'Got {lower}.')
        if upper and not re.match('\d+', str(upper)):
            raise InvalidUpperBound(f'Got {upper}.')
        self.lower = None if lower is None else float(lower)
        self.upper = None if upper is None else float(upper)

        if lower and upper:
            if self.lower == self.upper:
                raise InvalidCombination(
                    f'Lower and upper bound cannot be equal. Got {lower}={upper}')
            if self.lower > self.upper:
                raise InvalidCombination(
                    f'Lower bound cannot exceed upper bound. Got {lower}>{upper}')
        if not units:
            raise InvalidUnits('Got \'units\' is None')
        self.units = units
        self.lower_inclusive = lower_inclusive
        self.upper_inclusive = upper_inclusive
        self.lower_operator = (
            None if not self.lower else '<=' if self.lower_inclusive is True else '<')
        self.upper_operator = (
            None if not self.upper else '<=' if self.upper_inclusive is True else '<')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.description()})'

    def __str__(self):
        return self.description()

    def description(self, value=None, show_as_int=None, placeholder=None):
        placeholder = placeholder or 'x'
        if show_as_int:
            value = int(value) if value else placeholder
            lower = int(self.lower) if self.lower else ''
            upper = int(self.upper) if self.upper else ''
        else:
            value = float(value) if value else placeholder
            lower = float(self.lower) if self.lower else ''
            upper = float(self.upper) if self.upper else ''
        return (f'{lower}{self.lower_operator or ""}{value}'
                f'{self.upper_operator or ""}{upper} {self.units}')

    def in_bounds_or_raise(self, value, units=None, **kwargs):
        value = float(value)
        if units != self.units:
            raise InvalidUnits(f'Expected {self.units}. See {repr(self)}')
        condition = (
            f'{self.lower or ""}{self.lower_operator or ""}{value}'
            f'{self.upper_operator or ""}{self.upper or ""}')
        if not eval(condition):
            raise ValueBoundryError(condition)
        return True
