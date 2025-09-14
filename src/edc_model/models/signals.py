from django import dispatch
from django.db.models import expressions
from simple_history import signals


@dispatch.receiver(signals.pre_create_historical_record, dispatch_uid="simple_history_refresh")
def remove_f_expressions(sender, instance, history_instance, **kwargs) -> None:
    """Model with history manager fails to save if update contains
    an F() expression.

    You get a ValueError:
        ... F() expressions can only be used to update, not to insert.

    solution from:
    https://stackoverflow.com/questions/62343627/circumventing-f-expression-problem-of-
    django-simple-history-by-overriding-save/62369328#62369328
    """
    f_expression_fields = []
    for field in history_instance._meta.fields:
        field_value = getattr(history_instance, field.name)
        if isinstance(field_value, expressions.BaseExpression):
            f_expression_fields.append(field.name)

    if f_expression_fields:
        instance.refresh_from_db()
        for field_name in f_expression_fields:
            field_value = getattr(instance, field_name)
            setattr(history_instance, field_name, field_value)
