from .pill_bottle_model_mixin import PillBottleModelMixin


class PillBottle(PillBottleModelMixin):
    class Meta(PillBottleModelMixin.Meta):
        verbose_name = "Pill Bottle"
        verbose_name_plural = "Pill Bottles"
