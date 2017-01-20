
class PredicateError(Exception):
    pass


class Base:

    def get_value(self, *args, attr=None):
        """Returns a value by checking for the attr on each arg.

        Each arg in args may be a model instance, queryset, or None."""
        value = None
        for arg in args:
            try:
                value = getattr(arg, attr)
                if value:
                    break
            except AttributeError:
                try:
                    for obj in arg:
                        value = getattr(obj, attr)
                        if value:
                            break
                except (AttributeError, TypeError):
                    pass
        return value


class P(Base):

    """
    Simple predicate class.

    For example:

        predicate = P('gender', 'eq', 'MALE')
        predicate = P('referral_datetime', 'is not', None)
        predicate = P('age', '<=', 64)
    """

    funcs = {
        'is': lambda x, y: True if x is y else False,
        'is not': lambda x, y: True if x is not y else False,
        'gt': lambda x, y: True if x > y else False,
        '>': lambda x, y: True if x > y else False,
        'gte': lambda x, y: True if x >= y else False,
        '>=': lambda x, y: True if x >= y else False,
        'lt': lambda x, y: True if x < y else False,
        '<': lambda x, y: True if x < y else False,
        'lte': lambda x, y: True if x <= y else False,
        '<=': lambda x, y: True if x <= y else False,
        'eq': lambda x, y: True if x == y else False,
        'equals': lambda x, y: True if x == y else False,
        '==': lambda x, y: True if x == y else False,
        'neq': lambda x, y: True if x != y else False,
        '!=': lambda x, y: True if x != y else False,
    }

    def __init__(self, attr, operator, expected_value):
        self.attr = attr
        self.operator = operator
        self.expected_value = expected_value
        self.func = self.funcs.get(self.operator)

    def __repr__(self):
        return '<{}({}, {}, {})>'.format(
            self.__class__.__name__, self.attr, self.operator, self.expected_value)

    def __call__(self, *args):
        value = self.get_value(*args, attr=self.attr)
        return self.func(value, self.expected_value)


class PF(Base):
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
    def __init__(self, *attrs, func=None):
        self.attrs = attrs
        self.func = func

    def __call__(self, *args):
        values = []
        for attr in self.attrs:
            values.append(self.get_value(*args, attr=attr))
        return self.func(*values)

    def __repr__(self):
        return '<{}({}, {})>'.format(self.__class__.__name__, self.attr, self.func)
