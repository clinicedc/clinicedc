from django_pylabels.models import LabelSpecification as BaseLabelSpecification


class LabelSpecification(BaseLabelSpecification):
    class Meta:
        proxy = True
