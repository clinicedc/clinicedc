from typing import Any, Optional

from django.apps import apps as django_apps
from edc_reference import LongitudinalRefsets, site_reference_configs


class PredicateCollection:

    """A class that groups predicates for use in rules.

    For example:

        pc = Predicates()

        @register()
        class MyRequisitionRuleGroup(RequisitionRuleGroup):

            require_cd4 = RequisitionRule(
                predicate=pc.func_require_cd4,
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_panels=[cd4_panel])
    """

    app_label = "edc_metadata"
    visit_model = None

    def __init__(self) -> None:
        if not site_reference_configs.loaded:
            site_reference_configs.autodiscover()
        self.reference_model_cls = django_apps.get_model(
            site_reference_configs.get_reference_model(self.visit_model)
        )

    def values(
        self, value: Optional[Any] = None, field_name: Optional[str] = None, **kwargs
    ) -> list:
        """Returns a list of matching values or an empty list."""
        return self.exists(value=value, field_name=field_name, **kwargs)

    def exists(
        self,
        reference_name: Optional[str] = None,
        value: Optional[Any] = None,
        field_name: Optional[str] = None,
        **kwargs,
    ) -> list:
        """Returns a list of values, all or filtered, or an empty
        list.
        """
        refsets = self.refsets(reference_name=reference_name, **kwargs)
        if value:
            return refsets.fieldset(field_name).filter(value).values
        else:
            return refsets.fieldset(field_name).all().values

    def refsets(self, reference_name: Optional[str] = None, **options) -> Any:
        opts = dict(
            name=reference_name,
            visit_model=self.visit_model,
            reference_model_cls=self.reference_model_cls,
            **options,
        )
        refsets = LongitudinalRefsets(**opts)
        return refsets
