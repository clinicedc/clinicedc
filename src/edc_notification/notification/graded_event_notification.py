from .model_notification import ModelNotification


class GradedEventNotification(ModelNotification):

    grade = None
    model = None

    def notify_on_condition(self, instance=None, **kwargs):
        history = [
            obj.ae_grade for obj in instance.history.all().order_by("-history_date")
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
