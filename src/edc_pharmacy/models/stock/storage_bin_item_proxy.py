from .storage_bin_item import StorageBinItem


class StorageBinItemProxy(StorageBinItem):
    class Meta:
        proxy = True
        verbose_name = "Storage bin item"
        verbose_name_plural = "Storage bin items"
