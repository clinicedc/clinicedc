from typing import Optional

from django.apps import AppConfig
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class LoadListDataError(Exception):
    pass


def load_list_data(
    list_data: dict = None, model_name: Optional[str] = None, apps: Optional[AppConfig] = None
) -> int:
    """Loads data into a list model.

    List models have name, display_name where name
    is the unique field / stored field.

    Format:
        {model_name1: [(name1, display_name),
         (name2, display_name),...],
         model_name2: [(name1, display_name),
         (name2, display_name),...],
        ...}
    """
    apps = apps or django_apps
    if model_name:
        model_names = [model_name]
    else:
        model_names = [k for k in list_data.keys()]
    n = 0
    for model_name in model_names:
        try:
            model = apps.get_model(model_name)
            for display_index, value in enumerate(list_data.get(model_name)):
                store_value, display_value = value
                try:
                    obj = model.objects.get(name=store_value)
                except ObjectDoesNotExist:
                    model.objects.create(
                        name=store_value,
                        display_name=display_value,
                        display_index=display_index,
                    )
                else:
                    obj.display_name = display_value
                    obj.display_index = display_index
                    obj.save()
        except ValueError as e:
            raise LoadListDataError(f"{e} See {list_data.get(model_name)}.")
        n += 1
    return n
