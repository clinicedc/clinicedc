from .model_notification import ModelNotification


class GradedEventNotification(ModelNotification):

    grade = None
    model = None

    def notify_on_condition(self, instance=None, **kwargs):
        if instance._meta.label_lower == self.model:
            grading_history = [
                int(obj.ae_grade)
                for obj in instance.history.all().order_by('history_date')]
            grading_history.reverse()
            if grading_history:
                x = [int(x) for x in grading_history]
                if sum(x) != self.grade * 2 and x[0] == self.grade:
                    return True
        return False
