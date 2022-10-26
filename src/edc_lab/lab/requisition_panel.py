from __future__ import annotations

from typing import Type

from django.apps import apps as django_apps
from django.db import models

from .processing_profile import ProcessingProfile


class RequisitionPanelError(Exception):
    pass


class RequisitionPanelLookupError(Exception):
    pass


class InvalidProcessingProfile(Exception):
    pass


class PanelAttrs:

    """ "A simple class of panel name attributes."""

    def __init__(self, name: str = None, alpha_code: str = None) -> None:
        title = " ".join(name.split("_")).title()
        alpha_code = alpha_code or ""
        self.abbreviation = f"{name[0:2]}{name[-1:]}".upper()
        self.verbose_name = f"{title} {alpha_code} {self.abbreviation}".replace("  ", " ")


class RequisitionPanel:

    """A panel class that contains processing profile instances."""

    panel_attrs_cls = PanelAttrs
    requisition_model: str = None  # set by lab profile.add_panel
    lab_profile_name: str = None  # set by lab profile.add_panel
    panel_model: str = "edc_lab.panel"

    def __init__(
        self,
        name: str = None,
        processing_profile: ProcessingProfile = None,
        verbose_name: str = None,
        abbreviation: str = None,
        utest_ids: list[str | tuple] = None,
        is_poc=None,
        reference_range_collection_name=None,
    ) -> None:
        self._panel_model_obj = None
        self.name = name
        self.processing_profile = processing_profile
        panel_attrs = self.panel_attrs_cls(
            name=name, alpha_code=self.processing_profile.aliquot_type.alpha_code
        )
        self.abbreviation = abbreviation or panel_attrs.abbreviation
        self.verbose_name = verbose_name or panel_attrs.verbose_name
        self.utest_ids = utest_ids
        self.is_poc = is_poc
        # name for site_reportables collection, may also be set by LabProfile
        self.reference_range_collection_name = reference_range_collection_name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.aliquot_type})"

    def __str__(self):
        return self.verbose_name or self.name

    @property
    def aliquot_type(self):
        return self.processing_profile.aliquot_type

    @property
    def panel_model_cls(self):
        return django_apps.get_model(self.panel_model)

    @property
    def panel_model_obj(self):
        """Returns the underlying panel model instance."""
        if not self._panel_model_obj:
            self._panel_model_obj = self.panel_model_cls.objects.get(
                name=self.name, lab_profile_name=self.lab_profile_name
            )
        return self._panel_model_obj

    @property
    def requisition_model_cls(self) -> Type[models.Model]:
        """Returns the requisition model class associated with this
        panel (set by it's lab profile).
        """
        try:
            requisition_model_cls = django_apps.get_model(self.requisition_model)
        except (LookupError, ValueError, AttributeError) as e:
            raise RequisitionPanelLookupError(
                f"Invalid requisition model. requisition model="
                f"'{self.requisition_model}'. "
                f"See {repr(self)} or the lab profile {self.lab_profile_name}."
                f"Got {e}"
            )
        return requisition_model_cls

    @property
    def numeric_code(self) -> str:
        return self.aliquot_type.numeric_code

    @property
    def alpha_code(self) -> str:
        return self.aliquot_type.alpha_code


# TODO: panel should have some relation to the interface,
# e.g. a mapping of test_code to test_code on interface
#       for example CD4% = cd4_perc or VL = AUVL, VL = PMH
