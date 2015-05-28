from django.core.exceptions import ValidationError
from edc_content_type_map.models import ContentTypeMap


def is_visit_tracking_model(value):
    from edc_visit_tracking.models import BaseVisitTracking
    content_type_map = ContentTypeMap.objects.get(pk=value)
    if not issubclass(content_type_map.model_class(), BaseVisitTracking):
        raise ValidationError('Select a model that is a subclass of BaseVistTracking')
