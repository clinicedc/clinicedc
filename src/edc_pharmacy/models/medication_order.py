from .rx_refill import RxRefill


class MedicationOrder(RxRefill):
    class Meta:
        proxy = True
        verbose_name = "Medication order"
        verbose_name_plural = "Medication orders"
