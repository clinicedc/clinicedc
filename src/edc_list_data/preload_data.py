from typing import Optional

from django.apps import AppConfig
from django.core.management.color import color_style

from edc_list_data.load_model_data import load_model_data

from .load_list_data import load_list_data

style = color_style()


class PreloadData:
    def __init__(
        self,
        list_data: dict = None,
        model_data: dict = None,
        list_data_model_name: str = None,
        apps: AppConfig = None,
    ) -> None:
        self.list_data = list_data or {}
        self.model_data = model_data or {}
        self.item_count = 0
        if self.list_data:
            self.item_count += self.load_list_data(model_name=list_data_model_name, apps=apps)
        if self.model_data:
            self.item_count += self.load_model_data()

    def load_list_data(self, model_name: str = None, apps: Optional[AppConfig] = None) -> int:
        return load_list_data(self.list_data, model_name=model_name, apps=apps)

    def load_model_data(self, apps: Optional[AppConfig] = None) -> int:
        return load_model_data(self.model_data, apps=apps)
