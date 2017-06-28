from edc_metadata.constants import NOT_REQUIRED, REQUIRED

from ..constants import DO_NOTHING


class RuleLogicError(Exception):
    pass


class Logic(object):

    valid_results = [REQUIRED, NOT_REQUIRED, DO_NOTHING]

    def __init__(self, predicate=None, consequence=None, alternative=None,
                 comment=None, **kwargs):
        if not hasattr(predicate, '__call__'):
            raise RuleLogicError(
                'Predicate must be a callable. For example a '
                'predicate class such as "P" or "PF"')
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative
        self.comment = comment
        for result in [self.consequence, self.alternative]:
            if result not in self.valid_results:
                raise RuleLogicError(
                    f'Invalid result on rule. Expected one of '
                    f'{self.valid_results}. Got {result}.')

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.predicate}, '
                f'{self.consequence}, {self.alternative})')
