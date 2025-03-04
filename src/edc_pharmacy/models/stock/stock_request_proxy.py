from .stock_request import StockRequest


class StockRequestProxy(StockRequest):
    class Meta:
        proxy = True
        verbose_name = "Stock Request"
        verbose_name_plural = "Stock Requests"
