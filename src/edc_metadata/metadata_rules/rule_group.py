import sys
from typing import Any

from django.apps import apps as django_apps
from django.core.management.color import color_style

style = color_style()


class RuleGroupError(Exception):
    pass


class TargetModelConflict(Exception):
    pass


class RuleGroup:
    """Base class for CRF and Requisition rule groups."""

    @classmethod
    def get_rules(cls: Any) -> Any:
        return cls._meta.options.get("rules")

    @classmethod
    def validate(cls: Any) -> None:
        """Outputs to the console if a target model referenced in a rule
        does not exist.
        """
        # TODO: extend this list
        default_fields = ["gender"]

        if cls._meta.related_visit_model:
            cls._lookup_model(
                model=cls._meta.related_visit_model, category="related_visit_model"
            )

        # verify models exists
        if cls._meta.source_model:
            cls._lookup_model(model=cls._meta.source_model, category="source")

        for rule in cls.get_rules():
            for target_model in rule.target_models:
                cls._lookup_model(model=target_model, category="target")

        # verify fields referred to on source models
        # note: fields referenced in funcs in a predicate collection
        # are not verified here.
        if cls._meta.source_model:
            model_cls = cls._lookup_model(model=cls._meta.source_model, category="source")
            fields = [f.name for f in model_cls._meta.get_fields()]
            fields.extend(default_fields)
            for rule in cls.get_rules():
                for field_name in rule.field_names:
                    if field_name not in fields:
                        sys.stdout.write(
                            style.ERROR(
                                f"  (?) Field {cls._meta.source_model}.{field_name} "
                                f"is invalid.\n"
                            )
                        )

    @classmethod
    def _lookup_model(cls, model: str = None, category: str = None) -> Any:
        sys.stdout.write(f"  ( ) {model}\r")
        model_cls = None
        try:
            model_cls = django_apps.get_model(model)
        except LookupError:
            sys.stdout.write(style.ERROR(f"  (?) {model}. See {category} model in {cls}\n"))
        else:
            sys.stdout.write(f"  (*) {model}\n")
        return model_cls
