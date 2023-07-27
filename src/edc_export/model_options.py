from django.apps import apps as django_apps
from edc_list_data.model_mixins import ListModelMixin


class ModelOptions(dict):

    """A serializable object of a selection of model attrs."""

    def __init__(self, model: str = None):
        model_cls = django_apps.get_model(model)
        self.model: str = str(model)
        self.app_label: str = str(model_cls._meta.app_label)
        self.app_name: str = " ".join(model_cls._meta.app_label.split("_")).title()
        self.verbose_name: str = str(model_cls._meta.verbose_name)
        self.label_lower: str = str(model_cls._meta.label_lower)
        self.fields: list[str] = [f.name for f in model_cls._meta.get_fields()]
        self.is_historical: bool = model_cls._meta.label_lower.split(".")[1].startswith(
            "historical"
        )
        self.is_list_model: bool = issubclass(model_cls, (ListModelMixin,))
        self.db_table: str = str(model_cls._meta.db_table)
        dict.__init__(
            self,
            app_label=self.app_label,
            app_name=self.app_name,
            model=self.model,
            verbose_name=self.verbose_name,
            label_lower=self.label_lower,
            is_historical=self.is_historical,
            is_list_model=self.is_list_model,
            is_inline=self.is_inline,
            db_table=self.db_table,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.label_lower}')"

    @property
    def is_inline(self) -> bool:
        return False
