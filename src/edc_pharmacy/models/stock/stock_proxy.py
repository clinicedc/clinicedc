from .stock import Stock

__all__ = ["StockProxy"]


class StockProxy(Stock):
    class Meta:
        proxy = True
        verbose_name = "Stock"
        verbose_name_plural = "Stock"
