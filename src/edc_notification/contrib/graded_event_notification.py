from edc_notification.notification import Notification


class GradedEventNotification(Notification):

    grade = None
    model = None
    message_template = (
        'Do not reply to this email\n\n'
        '{test_message}'
        'A {instance._meta.verbose_name} has been submitted for patient '
        '{instance.subject_identifier} '
        'at site {instance.site.name} which may require '
        'your attention.\n\n'
        'Title: {display_name}\n\n'
        'You received this message because you are subscribed to receive these '
        'notifications in your user profile.\n\n'
        '{test_message}'
        'Thanks.')

    def callback(self):
        if self.instance._meta.label_lower == self.model:
            grading_history = [
                int(obj.ae_grade)
                for obj in self.instance.history.all().order_by('history_date')]
            grading_history.append(int(self.instance.ae_grade))
            if grading_history:
                x = [int(x) for x in grading_history][-2:]
                if sum(x) != self.grade * 2 and x[-1:][0] == self.grade:
                    return True
        return False
