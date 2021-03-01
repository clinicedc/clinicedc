from typing import Optional

from edc_model.stubs import BaseUuidHistoryModelStub

from .model_notification import ModelNotification


class GradedEventNotification(ModelNotification):

    grade: Optional[int] = None
    model: Optional[str] = None

    def notify_on_condition(self, instance: BaseUuidHistoryModelStub = None, **kwargs) -> bool:
        notify_on_condition = False
        if hasattr(instance, "ae_grade"):
            history = [
                obj.ae_grade
                for obj in instance.history.all().order_by("-history_date")  # type:ignore
            ]
            try:
                last_grade = history[1]
            except IndexError:
                notify_on_condition = str(history[0]) == str(self.grade)
            else:
                notify_on_condition = (
                    history[0] == str(self.grade) and last_grade != history[0]
                )
        return notify_on_condition
