from edc_metadata.constants import NOT_REQUIRED, REQUIRED

from ..constants import DO_NOTHING

from .exceptions import RuleError


class Logic(object):

    valid_results = [REQUIRED, NOT_REQUIRED, DO_NOTHING]

    def __init__(self, predicate=None, consequence=None, alternative=None, comment=None, **kwargs):
        if not hasattr(predicate, '__call__'):
            raise RuleError('Predicate must be a callable.')
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative
        self.comment = comment
        for result in [self.consequence, self.alternative]:
            if result not in self.valid_results:
                raise RuleError(
                    'Invalid result on rule. Expected one of {}. Got {}'.format(self.valid_results, result))

    def __repr__(self):
        return '<{}({}, {}, {})>'.format(self.__class__.__name__, self.predicate, self.consequence, self.alternative)

    @property
    def __doc__(self):
        return ('{0}. If True sets \'{{target_model}}\' to \'{1.consequence}\' otherwise \'{1.alternative}\'. '
                '{1.comment}').format(
                    (self.predicate.__doc__ or '<font color="red">missing docstring</font>'
                     ).strip('\n\r\t').replace('\n', ''), self)
