from django.core.exceptions import ValidationError

from edc.core.bhp_content_type_map.models import ContentTypeMap


def is_visit_tracking_model(value):
    from edc_visit_tracking.models import VisitTrackingModelMixin
    content_type_map = ContentTypeMap.objects.get(pk=value)
    if not issubclass(content_type_map.model_class(), VisitTrackingModelMixin):
        raise ValidationError('Select a model that is a subclass of BaseVistTracking')
