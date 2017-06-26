from django.core.exceptions import ObjectDoesNotExist

from ..constants import REQUISITION

from .exceptions import RequisitionRuleGroupErrror
from .rule import Rule


class RequisitionRule(Rule):

    def __init__(self, target_model, target_panels, **kwargs):
        self.metadata_category = REQUISITION
        self.target_model = target_model
        self.target_panels = target_panels
        super(RequisitionRule, self).__init__(**kwargs)

    def run_rules(self, target_model, visit, *args):
        for panel in self.target_panels:
            try:
                panel_name = panel.name
            except AttributeError as e:
                raise RequisitionRuleGroupErrror(
                    f'{e} Expected panel instance. Got panel={panel}.')
            try:
                target_model.objects.get_for_visit(
                    visit, panel_name=panel_name)
            except target_model.DoesNotExist:
                entry_status = self.evaluate(visit, *args)
                try:
                    visit.run_rules_for_model(
                        target_model._meta.label_lower,
                        entry_status=entry_status,
                        panel_name=panel_name)
                except ObjectDoesNotExist:
                    pass
