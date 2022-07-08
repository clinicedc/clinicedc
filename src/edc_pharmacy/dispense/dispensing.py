from django.db.models import Sum


class DispenseError(Exception):
    pass


# TODO: dispense against stock for site / central, etc
class Dispensing:
    def __init__(
        self,
        rx_refill,
        dispensed=None,
        exclude_id=None,
    ):
        """Dispense against an existing refill with remaining items"""
        self.exclude_id = exclude_id
        self.rx_refill = rx_refill
        self.dispensed = dispensed

    @property
    def remaining(self) -> float:
        value = 0.0
        if self.rx_refill.total:
            value = float(self.rx_refill.total) - float(self.total_dispensed)
        if value < 0.0:
            raise DispenseError(
                "Attempt to dispense more than remaining on refill. "
                f"Remaining={value}. Got {self.dispensed}."
            )
        return value

    @property
    def total_dispensed(self) -> float:
        """Returns the total dispensed for this refill"""
        options = {}
        if self.rx_refill.total:
            if self.exclude_id:
                options = dict(id=self.exclude_id)
            aggregate = self.rx_refill.dispensinghistory_set.filter(**options).aggregate(
                Sum("dispensed")
            )
            return float(aggregate.get("dispensed__sum") or 0.0)
        return 0.0
