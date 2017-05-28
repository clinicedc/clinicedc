from ..ordered_collection import OrderedCollection
from ..validator import get_model


class SchedulesCollectionError(Exception):
    pass


class SchedulesCollection(OrderedCollection):

    key = 'name'
    ordering_attr = 'sequence'

    def get_schedule(self, model=None, schedule_name=None, **kwargs):
        """Returns a schedule or raises; by name, by enrollment/disenrollment model
        or by model label_lower.
        """
        schedule = None
        if model:
            schedule = self._get_schedule_by_model(model=model)
        elif schedule_name:
            schedule = self.get(schedule_name)
        if not schedule:
            raise SchedulesCollectionError(
                f'Schedule does not exist. Using model={model}, schedule_name={schedule_name}.')
        return schedule

    def _get_schedule_by_model(self, model=None):
        """Returns a schedule or None looked up using the model
        class or label_lower.
        """
        schedule = None
        try:
            model = get_model(model=model)
        except LookupError as e:
            raise SchedulesCollectionError(f'Invalid model for schedule. Got {e}')
        for schedule in self.values():
            if schedule.enrollment_model == model:
                return schedule
            elif schedule.disenrollment_model == model:
                return schedule
        return None
