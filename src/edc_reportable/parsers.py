import re

from collections import OrderedDict


class ParserError(Exception):
    pass


def unparse(**kwargs):

    lower = kwargs.get('lower') or ''
    upper = kwargs.get('upper') or ''
    lower_op = (
        '' if not lower else '<=' if kwargs.get('lower_inclusive') else '<')
    upper_op = (
        '' if not upper else '<=' if kwargs.get('upper_inclusive') else '<')
    gender = kwargs.get('gender', '')
    age_lower = kwargs.get('age_lower', '')
    age_upper = kwargs.get('age_upper', '')
    age_lower_op = (
        '' if not age_lower
        else '<=' if kwargs.get('age_lower_inclusive') else '<')
    age_upper_op = (
        '' if not age_upper
        else '<=' if kwargs.get('age_upper_inclusive') else '<')
    age = ('' if not age_lower and not age_upper
           else f'{age_lower}{age_lower_op}AGE{age_upper_op}{age_upper}')
    return (f'{lower}{lower_op}x{upper_op}{upper} {gender} {age}'.rstrip())


def parse(phrase=None, **kwargs):

    pattern = '(([\d+\.\d+]|[\.\d+])?(<|<=)?)+x((<|<=)?([\d+\.\d+]|[\.\d+])+)?'

    def _parse(string):
        inclusive = True if '=' in string else None
        try:
            value = float(string.replace('<', '').replace('=', ''))
        except ValueError:
            value = None
        return value, inclusive
    phrase = phrase.replace(' ', '')
    match = re.match(pattern, phrase)
    if not match or match.group() != phrase:
        raise ParserError(
            f'Invalid. Got {phrase}. Expected, e.g, 11<x<22, '
            f'11<=x<22, 11<x<=22, 11<x, 11<=x, x<22, x<=22, etc.')
    left, right = phrase.replace(' ', '').split('x')
    lower, lower_inclusive = _parse(left)
    upper, upper_inclusive = _parse(right)
    ret = OrderedDict(
        lower=lower,
        lower_inclusive=lower_inclusive,
        upper=upper,
        upper_inclusive=upper_inclusive,
        **kwargs)
    for k, v in ret.items():
        setattr(ret, k, v)
    return ret
