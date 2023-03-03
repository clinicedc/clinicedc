from django.apps import apps


def get_model_from_table_name(table_name: str):
    return next((m for m in apps.get_models() if m._meta.db_table == table_name), None)
