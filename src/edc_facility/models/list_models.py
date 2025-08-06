from edc_list_data.model_mixins import ListModelMixin


class HealthFacilityTypes(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Health Facility Type"
        verbose_name_plural = "Health Facility Types"
