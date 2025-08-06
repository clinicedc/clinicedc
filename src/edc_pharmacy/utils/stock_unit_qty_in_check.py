from edc_pharmacy.models import Stock


def stock_unit_qty_in_check():
    """Check for any buckets where unit_qty_in < unit_qty_out

    Assumes 128 tabs
    """
    for obj in Stock.objects.filter(container__container_type__name="bucket"):
        stock_code = obj.code
        stock_unit_qty_in = obj.unit_qty_in
        stock_unit_qty_out = obj.unit_qty_out
        from_stock_count = Stock.objects.filter(from_stock__code=obj.code).count() * 128

        if not stock_unit_qty_in >= stock_unit_qty_out:
            print(stock_code, stock_unit_qty_in, stock_unit_qty_out, from_stock_count)
            print(f"**Error stock_code={stock_code}")
