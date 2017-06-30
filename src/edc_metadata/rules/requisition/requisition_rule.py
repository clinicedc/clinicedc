from edc_metadata.constants import REQUISITION

from ..rule import Rule
from ..rule_evaluator import RuleEvaluator


class RequisitionRuleEvaluatorError(Exception):
    pass


class RequisitionRuleEvaluator(RuleEvaluator):

    def __init__(self, source_panel=None, **kwargs):
        self.source_panel = source_panel
        super().__init__(**kwargs)

    @property
    def source_object(self):
        """Returns the source model instance or None.
        """
        if not self._source_object:
            if self.source_model:
                opts = {}
                if self.source_panel:
                    opts = dict(panel_name=self.source_panel)
                try:
                    self._source_object = self.source_model.objects.get_for_visit(
                        self.visit, **opts)
                except self.source_model.DoesNotExist:
                    pass
                except AttributeError as e:
                    raise RequisitionRuleEvaluatorError(
                        f'Model missing required manager method \'get_for_visit\'. '
                        f'See \'{self.source_model}\'. Got {e}') from e
        return self._source_object


class RequisitionRule(Rule):

    rule_evaluator_cls = RequisitionRuleEvaluator

    def __init__(self, source_panel=None, target_panels=None, **kwargs):
        self.metadata_category = REQUISITION
        try:
            self.target_panels = [p.name for p in target_panels]
        except AttributeError:
            self.target_panels = target_panels
        try:
            self.source_panel = source_panel.name
        except AttributeError:
            self.source_panel = source_panel
        super().__init__(**kwargs)
