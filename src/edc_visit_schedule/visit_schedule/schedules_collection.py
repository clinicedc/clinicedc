from ..ordered_collection import OrderedCollection
from ..schedule import Schedule


class SchedulesCollectionError(Exception):
    pass


class SchedulesCollection(OrderedCollection):
    key = "name"
    ordering_attr = "sequence"

    def __init__(self, visit_schedule_name: str, *args, **kwargs) -> None:
        self.visit_schedule_name = visit_schedule_name
        super().__init__(*args, **kwargs)

    def get_schedule(
        self, model: str | None = None, schedule_name: str | None = None
    ) -> Schedule:
        """Returns a schedule or raises; by name, by onschedule/offschedule model
        or by model label_lower.
        """
        schedule = None
        if model:
            model = model.lower()
            for item in self.values():
                if model in (item.onschedule_model, item.offschedule_model):
                    schedule = item
                if schedule:
                    break
        elif schedule_name:
            schedule = self.get(schedule_name)
        if not schedule:
            raise SchedulesCollectionError(
                f"Schedule does not exist. Using model={model}, schedule_name={schedule_name}."
            )
        return schedule

    def validate(self) -> None:
        for schedule in self.values():
            schedule.validate(visit_schedule_name=self.visit_schedule_name)
