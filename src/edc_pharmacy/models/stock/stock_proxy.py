from .stock import Stock


class StockProxy(Stock):
    class Meta:
        proxy = True
