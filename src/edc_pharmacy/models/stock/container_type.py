from edc_list_data.model_mixins import ListModelMixin


class ContainerType(ListModelMixin):

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.capitalize()
        super().save(*args, **kwargs)

    class Meta(ListModelMixin.Meta):
        verbose_name = "Container type"
        verbose_name_plural = "Container types"
