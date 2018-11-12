from .model_notification import ModelNotification


class GradedEventNotification(ModelNotification):

    grade = None
    model = None

    def notify_on_condition(self, instance=None, **kwargs):
        notify_on_condition = False
        history = [
            int(obj.ae_grade)
            for obj in instance.history.all().order_by('history_date')]
        history.reverse()
        if history:
            try:
                last_grade = history[1]
            except IndexError:
                notify_on_condition = history[0] == self.grade
            else:
                notify_on_condition = (
                    history[0] == self.grade and last_grade != history[0])
        return notify_on_condition
