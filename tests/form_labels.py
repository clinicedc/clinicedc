from edc_constants.constants import NO
from edc_form_label import CustomLabelCondition


class MyCustomLabelCondition(CustomLabelCondition):
    def check(self, **kwargs):
        if self.previous_obj:
            return self.previous_obj.circumcised == NO
        return False
