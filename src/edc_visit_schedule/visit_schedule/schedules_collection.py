from ..ordered_collection import OrderedCollection
from .model_validator import get_model


class SchedulesCollectionError(Exception):
    pass


class SchedulesCollection(OrderedCollection):

    key = 'name'
    ordering_attr = 'sequence'

    def get_schedule(self, model=None, schedule_name=None):
        """Returns a schedule by name, by enrollment/disenrollment model
        or model label_lower.
        """
        schedule = None
        if model:
            schedule = self.get_schedule_by_model(model=model)
        elif schedule_name:
            schedule = self.get(schedule_name)
        return schedule

    def get_schedule_by_model(self, model=None):
        """Returns a schedule or None looked up using the model
        class or label_lower.
        """
        schedule = None
        try:
            model = get_model(model=model)
        except LookupError as e:
            raise SchedulesCollectionError(f'Invalid model for schedule. Got{e}')
        for schedule in self.values():
            if schedule.enrollment_model == model:
                return schedule
            elif schedule.disenrollment_model == model:
                return schedule
        return None
