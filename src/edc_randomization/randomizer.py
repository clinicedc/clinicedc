from __future__ import annotations

import contextlib
import warnings
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q

from edc_registration.utils import get_registered_subject_model_cls

from .constants import (
    DEFAULT_ASSIGNMENT_DESCRIPTION_MAP,
    DEFAULT_ASSIGNMENT_MAP,
    RANDOMIZED,
)
from .randomization_list_importer import (
    RandomizationListAlreadyImported,
    RandomizationListImporter,
)
from .utils import get_randomization_list_path

if TYPE_CHECKING:
    from edc_registration.models import RegisteredSubject


class InvalidAssignmentDescriptionMap(Exception):  # noqa: N818
    pass


class RandomizationListFileNotFound(Exception):  # noqa: N818
    pass


class RandomizationListNotLoaded(Exception):  # noqa: N818
    pass


class RandomizationError(Exception):
    pass


class AlreadyRandomized(ValidationError):  # noqa: N818
    pass


class AllocationError(Exception):
    pass


class Randomizer:
    """Selects and uses the next available slot in model
    RandomizationList (cls.model) for this site. A slot is used
    when the subject identifier is not None.

    This is the default randomizer class and is registered with
    `site_randomizer` by default. To prevent registration set
    settings.EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False.

    assignment_map: {<assignment:str)>: <allocation:int>, ...}
    assignment_description_map: {<assignment:str)>: <description:str>, ...}


    Usage:
        Randomizer(
            subject_identifier=subject_identifier,
            report_datetime=report_datetime,
            site=site,
            user=user,
            **kwargs,
        ).randomize()

    It is better to access this class via the site_randomizer through a signal
    on something like the subject_consent:

        site_randomizers.randomize(
            "default",
            subject_identifier=instance.subject_identifier,
            report_datetime=instance.consent_datetime,
            site=instance.site,
            user=instance.user_created,
            gender=instance.gender)



    """

    name: str = "default"
    model: str = "edc_randomization.randomizationlist"
    assignment_map: dict[str, int] = getattr(
        settings, "EDC_RANDOMIZATION_ASSIGNMENT_MAP", DEFAULT_ASSIGNMENT_MAP
    )
    assignment_description_map: dict[str, str] = getattr(
        settings,
        "EDC_RANDOMIZATION_ASSIGNMENT_DESCRIPTION_MAP",
        DEFAULT_ASSIGNMENT_DESCRIPTION_MAP,
    )
    filename: str = "randomization_list.csv"
    randomizationlist_folder: Path | str = get_randomization_list_path()
    extra_csv_fieldnames: list[str] | None = None
    trial_is_blinded: bool = True
    importer_cls: Any = RandomizationListImporter
    apps = None  # if not using django_apps

    def __init__(
        self,
        identifier: str | None = None,
        subject_identifier: str | None = None,
        identifier_attr: str | None = None,
        identifier_object_name: str | None = None,
        report_datetime: datetime | None = None,
        site: Any | None = None,
        user: str | None = None,
        **kwargs,  # noqa: ARG002
    ):
        self._model_obj = None
        self._registration_obj = None
        self.identifier_attr = identifier_attr or "subject_identifier"
        self.identifier_object_name = identifier_object_name or "subject"
        setattr(self, self.identifier_attr, identifier or subject_identifier)
        self.allocated_datetime = report_datetime
        self.site = site
        self.user = user
        self.validate_assignment_description_map()
        self.import_list(overwrite=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name},{self.randomizationlist_folder})"

    def __str__(self):
        return f"<{self.name} for file {self.randomizationlist_folder}>"

    @classmethod
    def get_assignment(cls, subject_identifier: str) -> str | None:
        try:
            obj = cls.model_cls().objects.get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            pass
        else:
            return obj.assignment
        return None

    def randomize(self):
        """Randomize a subject.

        Will raise RandomizationError if general problems;
        Will raise AlreadyRandomized if already randomized.
        """
        self.raise_if_already_randomized()
        required_instance_attrs = dict(
            allocated_datetime=self.allocated_datetime,
            user=self.user,
            site=self.site,
            **self.identifier_opts,
            **self.extra_required_instance_attrs,
        )

        if not all(required_instance_attrs.values()):
            raise RandomizationError(
                f"Randomization failed. Insufficient data. Got {required_instance_attrs}."
            )
        setattr(
            self.model_obj,
            self.identifier_attr,
            getattr(self, self.identifier_attr),
        )
        self.model_obj.allocated_datetime = self.allocated_datetime
        self.model_obj.allocated_user = self.user
        self.model_obj.allocated_site = self.site
        self.model_obj.allocated = True
        self.model_obj.save()
        # requery
        self._model_obj = self.model_cls().objects.get(
            allocated=True,
            allocated_datetime=self.allocated_datetime,
            **self.identifier_opts,
        )
        self.registration_obj.sid = self.sid
        self.registration_obj.randomization_datetime = self.model_obj.allocated_datetime
        self.registration_obj.registration_status = RANDOMIZED
        self.registration_obj.randomization_list_model = self.model_obj._meta.label_lower
        self.registration_obj.save()
        # requery
        self._registration_obj = self.get_registration_model_cls().objects.get(
            sid=self.model_obj.sid, **self.identifier_opts
        )

    @property
    def identifier_opts(self) -> dict[str, str]:
        return {self.identifier_attr: getattr(self, self.identifier_attr)}

    @classmethod
    def get_registration_model_cls(cls) -> type[RegisteredSubject]:
        return get_registered_subject_model_cls()

    @property
    def extra_required_instance_attrs(self):
        """Returns a dict of extra attributes that must have
        value on self.
        """
        return {}

    @property
    def sid(self):
        """Returns the SID."""
        if not self.model_obj.sid:
            raise RandomizationError(
                f"SID cannot be None. See {self.model_obj}. Got {self.model_obj.sid}"
            )
        return self.model_obj.sid

    @property
    def extra_model_obj_options(self):
        """Returns a dict of extra key/value pair for filtering the
        "rando" model.
        """
        return {}

    @classmethod
    def model_cls(cls):
        return (cls.apps or django_apps).get_model(cls.model)

    @property
    def model_obj(self):
        """Returns a "rando" model instance by selecting
        the next available SID.

        (e.g. RandomizationList)
        """
        if not self._model_obj:
            try:
                obj = self.model_cls().objects.get(**self.identifier_opts)
            except ObjectDoesNotExist as e:
                opts = dict(site_name=self.site.name, **self.extra_model_obj_options)
                self._model_obj = (
                    self.model_cls()
                    .objects.filter(**{f"{self.identifier_attr}__isnull": True}, **opts)
                    .order_by("sid")
                    .first()
                )
                if not self._model_obj:
                    fld_str = ", ".join([f"{k}=`{v}`" for k, v in opts.items()])
                    raise AllocationError(
                        f"Randomization failed. No additional SIDs available for {fld_str}."
                    ) from e
            else:
                raise AlreadyRandomized(
                    f"{self.identifier_object_name.title()} already randomized. "
                    f"Got {getattr(obj, self.identifier_attr)} SID={obj.sid}. "
                    f"Something is wrong. Are "
                    f"{self.get_registration_model_cls()._meta.label_lower} and "
                    f"{self.model_cls()._meta.label_lower} out of sync?.",
                    code=self.model_cls()._meta.label_lower,
                )
        return self._model_obj

    def raise_if_already_randomized(self) -> Any:
        """Forces a query, will raise if already randomized."""
        return self.registration_obj

    def validate_assignment_description_map(self) -> None:
        """Raises an exception if the assignment description map
        has extra or missing keys.

        Compares with the assignment map.
        """
        if sorted(list(self.assignment_map.keys())) != sorted(
            list(self.assignment_description_map.keys())
        ):
            raise InvalidAssignmentDescriptionMap(
                f"Invalid assignment description. See randomizer {self.name}. "
                f"Got {self.assignment_description_map}."
            )

    def get_unallocated_registration_obj(self):
        """Returns an unallocated registration model instance
        or raises.

        Called by `registration_obj`.
        """
        return self.get_registration_model_cls().objects.get(
            (Q(sid__isnull=True) | Q(sid="")), **self.identifier_opts
        )

    @property
    def registration_obj(self):
        """Returns an unrandomized instance of the registration model
        for this identifier or raises.

        By default, if SID is null, the instance has not been randomized.

        (e.g. RegisteredSubject).
        """

        if not self._registration_obj:
            try:
                self._registration_obj = self.get_unallocated_registration_obj()
            except ObjectDoesNotExist as e:
                try:
                    obj = self.get_registration_model_cls().objects.get(**self.identifier_opts)
                except ObjectDoesNotExist as e:
                    raise RandomizationError(
                        f"{self.identifier_object_name.title()} does not exist. "
                        f"Got {getattr(self, self.identifier_attr)}"
                    ) from e
                else:
                    raise AlreadyRandomized(
                        f"{self.identifier_object_name.title()} already randomized. "
                        f"See {self.get_registration_model_cls()._meta.verbose_name}. "
                        f"Got {getattr(obj, self.identifier_attr)} "
                        f"SID={obj.sid}",
                        code=self.get_registration_model_cls()._meta.label_lower,
                    ) from e
        return self._registration_obj

    @property
    def registered_subject(self):
        warnings.warn(
            "This property is decrecated in favor of `registration_obj`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.registration_obj

    @classmethod
    def get_extra_list_display(cls) -> tuple[tuple[int, str], ...]:
        """Returns a list of tuples of (pos, field name) for ModelAdmin."""
        return ()

    @classmethod
    def get_extra_list_filter(cls) -> tuple[tuple[int, str], ...]:
        """Returns a list of tuples of (pos, field name) for ModelAdmin."""
        return cls.get_extra_list_display()

    @classmethod
    def get_randomizationlist_path(cls) -> Path:
        return Path(cls.randomizationlist_folder) / cls.filename

    @classmethod
    def import_list(cls, **kwargs) -> tuple[int, str]:
        result = (0, "")
        if not cls.get_randomizationlist_path().exists():
            raise RandomizationListFileNotFound(
                "Randomization list file not found. "
                f"Got `{cls.get_randomizationlist_path()}`. See Randomizer {cls.name}."
            )
        with contextlib.suppress(RandomizationListAlreadyImported):
            result = cls.importer_cls(
                assignment_map=cls.assignment_map,
                randomizationlist_path=cls.get_randomizationlist_path(),
                randomizer_model_cls=cls.model_cls(),
                randomizer_name=cls.name,
                extra_csv_fieldnames=cls.extra_csv_fieldnames,
                **kwargs,
            ).import_list(**kwargs)
        return result

    @classmethod
    def verify_list(cls, **kwargs) -> list[str]:
        return cls.importer_cls.verifier_cls(
            assignment_map=cls.assignment_map,
            randomizationlist_path=cls.get_randomizationlist_path(),
            randomizer_model_cls=cls.model_cls(),
            randomizer_name=cls.name,
            **kwargs,
        ).messages
