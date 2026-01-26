from sequences import get_next_value

from .storage_bin import StorageBin


class StorageBinProxy(StorageBin):
    def _get_bin_identifier(self):
        return (
            f"{get_next_value(self._meta.proxy_for_model._meta.label_lower):06d}"
            if not self.id
            else None
        )

    class Meta:
        proxy = True
        verbose_name = "Central Storage bin"
        verbose_name_plural = "Central Storage bins"
