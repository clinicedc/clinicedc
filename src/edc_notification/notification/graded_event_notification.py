from typing import Optional

from .model_notification import ModelNotification


class GradedEventNotification(ModelNotification):

    grade: Optional[int] = None
    model: Optional[str] = None
    create_fields = ["ae_grade"]
    update_fields = ["ae_grade"]

    def field_value_condition_on_create(self, field, current_value):
        return str(current_value) == str(self.grade)

    def field_value_condition_on_update(self, field, previous_value, current_value):
        """Returns True if the value has changed and matches self.grade"""
        return str(previous_value) != str(current_value) and str(current_value) == str(
            self.grade
        )
