from __future__ import annotations

from edc_reference import ReferenceGetter


class RuleGroupMetaError(Exception):
    pass


class RuleGroupMetaOptions:
    """Class to prepare the "meta" instance with the Meta class
    attributes.

    Adds default options if they were not declared on Meta class.

    """

    reference_getter_cls = ReferenceGetter

    def __init__(self, group_name: str, attrs: dict) -> None:
        meta = attrs.pop("Meta", None)
        # assert metaclass was declared on the rule group
        if not meta:
            raise AttributeError(f"Missing Meta class. See {group_name}")
        # add default options if they do not exist
        for attr in self.default_meta_options:
            try:
                getattr(meta, attr)
            except AttributeError:
                setattr(meta, attr, None)
        # populate options dictionary
        self.options = {k: getattr(meta, k) for k in meta.__dict__ if not k.startswith("_")}
        # raise on any unknown attributes declared on the Meta class
        for meta_attr in self.options:
            if meta_attr not in [
                k for k in self.default_meta_options if not k.startswith("_")
            ]:
                raise RuleGroupMetaError(
                    f"Invalid _meta attr. Got '{meta_attr}'. See {group_name}."
                )
        # default app_label to current module if not declared
        module_name = attrs.get("__module__").split(".")[0]
        self.app_label = self.options.get("app_label", module_name)
        # reference model helper class
        self.options.update(reference_getter_cls=self.reference_getter_cls)
        # source model
        self.source_model = self.options.get("source_model")
        if self.source_model:
            if len(self.source_model.split(".")) != 2:
                self.source_model = f"{self.app_label}.{self.source_model}"
            self.options.update(source_model=self.source_model)

    @property
    def default_meta_options(self) -> list[str]:
        return ["app_label", "source_model"]
