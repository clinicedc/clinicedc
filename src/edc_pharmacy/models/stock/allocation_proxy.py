from .allocation import Allocation

__all__ = ["AllocationProxy"]


class AllocationProxy(Allocation):
    class Meta:
        proxy = True
        verbose_name = "Allocation"
        verbose_name_plural = "Allocation"
