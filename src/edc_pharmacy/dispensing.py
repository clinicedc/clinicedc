from django.db.models import Sum


class DispenseError(Exception):
    pass


class Dispensing:
    def __init__(
        self,
        rx_refill,
        dispensed=None,
        exclude_id=None,
    ):
        self.exclude_id = exclude_id
        self.rx_refill = rx_refill
        self.dispensed = dispensed

    def check(self):
        if self.remaining < float(self.dispensed):
            raise DispenseError(
                "Attempt to dispense more than remaining on prescription. "
                f"Remaining={self.remaining}. Got {self.dispensed}."
            )

    @property
    def remaining(self) -> float:
        if self.rx_refill.total:
            return float(self.rx_refill.total) - float(self.total_dispensed)
        return 0.0

    @property
    def total_dispensed(self) -> float:
        options = {}
        if self.rx_refill.total:
            if self.exclude_id:
                options = dict(id=self.exclude_id)
            aggregate = self.rx_refill.dispensinghistory_set.filter(
                **options
            ).aggregate(Sum("dispensed"))
            return float(aggregate.get("dispensed__sum") or 0.0)
        return 0.0
