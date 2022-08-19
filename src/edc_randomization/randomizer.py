import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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


class InvalidAssignmentDescriptionMap(Exception):
    pass


class RandomizationListFileNotFound(Exception):
    pass


class RandomizationListNotLoaded(Exception):
    pass


class RandomizationError(Exception):
    pass


class AlreadyRandomized(ValidationError):
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

    Its better to access this class via the site_randomizer through a signal
    on something like the subject_consent:

        site_randomizers.randomize(
            "default",
            subject_identifier=instance.subject_identifier,
            report_datetime=instance.consent_datetime,
            site=instance.site,
            user=instance.user_created,
            gender=instance.gender,
        )


    """

    name: str = "default"
    model: str = "edc_randomization.randomizationlist"
    assignment_map: Dict[str, int] = getattr(
        settings, "EDC_RANDOMIZATION_ASSIGNMENT_MAP", DEFAULT_ASSIGNMENT_MAP
    )
    assignment_description_map: Dict[str, str] = getattr(
        settings,
        "EDC_RANDOMIZATION_ASSIGNMENT_DESCRIPTION_MAP",
        DEFAULT_ASSIGNMENT_DESCRIPTION_MAP,
    )
    filename: str = "randomization_list.csv"
    randomizationlist_folder: str = getattr(
        settings, "EDC_RANDOMIZATION_LIST_PATH", os.path.join(settings.BASE_DIR, ".etc")
    )
    extra_csv_fieldnames: Optional[List[str]] = None
    is_blinded_trial: bool = True
    importer_cls: Any = RandomizationListImporter
    apps = None  # if not using django_apps

    def __init__(
        self,
        subject_identifier: str = None,
        report_datetime: datetime = None,
        site: Any = None,
        user: str = None,
        **kwargs,
    ):
        self._model_obj = None
        self._registered_subject = None
        self.subject_identifier = subject_identifier
        self.allocated_datetime = report_datetime
        self.site = site
        self.user = user
        self.validate_assignment_description_map()
        self.import_list(overwrite=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name},{self.randomizationlist_folder})"

    def __str__(self):
        return f"<{self.name} for file {self.randomizationlist_folder}>"

    def randomize(self):
        """Randomize a subject.

        Will raise RandomizationError if general problems;
        Will raise AlreadyRandomized if already randomized.
        """
        self.raise_if_already_randomized()

        required_instance_attrs = dict(
            subject_identifier=self.subject_identifier,
            allocated_datetime=self.allocated_datetime,
            user=self.user,
            site=self.site,
            **self.extra_required_instance_attrs,
        )

        if not all(required_instance_attrs.values()):
            raise RandomizationError(
                f"Randomization failed. Insufficient data. Got {required_instance_attrs}."
            )
        self.model_obj.subject_identifier = self.subject_identifier
        self.model_obj.allocated_datetime = self.allocated_datetime
        self.model_obj.allocated_user = self.user
        self.model_obj.allocated_site = self.site
        self.model_obj.allocated = True
        self.model_obj.save()
        # requery
        self._model_obj = self.model_cls().objects.get(
            subject_identifier=self.subject_identifier,
            allocated=True,
            allocated_datetime=self.allocated_datetime,
        )
        self.registered_subject.sid = self.sid
        self.registered_subject.randomization_datetime = self.model_obj.allocated_datetime
        self.registered_subject.registration_status = RANDOMIZED
        self.registered_subject.randomization_list_model = self.model_obj._meta.label_lower
        self.registered_subject.save()
        # requery
        self._registered_subject = get_registered_subject_model_cls().objects.get(
            subject_identifier=self.subject_identifier, sid=self.model_obj.sid
        )

    @property
    def extra_required_instance_attrs(self):
        """Returns a dict of extra attributes that must have
        value on self.
        """
        return {}

    @property
    def sid(self):
        """Returns the SID."""
        if self.model_obj.sid is None:
            raise RandomizationError(f"SID cannot be None. See {self.model_obj}.")
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
        """
        if not self._model_obj:
            try:
                obj = self.model_cls().objects.get(subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                opts = dict(site_name=self.site.name, **self.extra_model_obj_options)
                self._model_obj = (
                    self.model_cls()
                    .objects.filter(subject_identifier__isnull=True, **opts)
                    .order_by("sid")
                    .first()
                )
                if not self._model_obj:
                    fld_str = ", ".join([f"{k}=`{v}`" for k, v in opts.items()])
                    raise AllocationError(
                        f"Randomization failed. No additional SIDs available for {fld_str}."
                    )
            else:
                raise AlreadyRandomized(
                    "Subject already randomized. "
                    f"Got {obj.subject_identifier} SID={obj.sid}. "
                    "Something is wrong. Are registered_subject and "
                    f"{self.model_cls()._meta.label_lower} out of sync?.",
                    code=self.model_cls()._meta.label_lower,
                )
        return self._model_obj

    def raise_if_already_randomized(self) -> Any:
        """Forces a query, will raise if already randomized."""
        return self.registered_subject

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

    @property
    def registered_subject(self):
        """Returns an instance of the registered subject model."""
        if not self._registered_subject:
            try:
                self._registered_subject = get_registered_subject_model_cls().objects.get(
                    subject_identifier=self.subject_identifier, sid__isnull=True
                )
            except ObjectDoesNotExist:
                try:
                    obj = get_registered_subject_model_cls().objects.get(
                        subject_identifier=self.subject_identifier
                    )
                except ObjectDoesNotExist:
                    raise RandomizationError(
                        f"Subject does not exist. Got {self.subject_identifier}"
                    )
                else:
                    raise AlreadyRandomized(
                        "Subject already randomized. See RegisteredSubject. "
                        f"Got {obj.subject_identifier} "
                        f"SID={obj.sid}",
                        code=get_registered_subject_model_cls()._meta.label_lower,
                    )
        return self._registered_subject

    @classmethod
    def get_extra_list_display(cls) -> Tuple[Tuple[int, str], ...]:
        """Returns a list of tuples of (pos, field name) for ModelAdmin."""
        return ()

    @classmethod
    def get_extra_list_filter(cls) -> Tuple[Tuple[int, str], ...]:
        """Returns a list of tuples of (pos, field name) for ModelAdmin."""
        return cls.get_extra_list_display()

    @classmethod
    def randomizationlist_path(cls) -> str:
        return os.path.expanduser(os.path.join(cls.randomizationlist_folder, cls.filename))

    @classmethod
    def import_list(cls, **kwargs) -> Tuple[int, str]:
        result = (0, "")
        if not os.path.exists(cls.randomizationlist_path()):
            raise RandomizationListFileNotFound(
                "Randomization list file not found. "
                f"Got `{cls.randomizationlist_path()}`. See Randomizer {cls.name}."
            )
        try:
            result = cls.importer_cls(
                assignment_map=cls.assignment_map,
                randomizationlist_path=cls.randomizationlist_path(),
                randomizer_model_cls=cls.model_cls(),
                randomizer_name=cls.name,
                extra_csv_fieldnames=cls.extra_csv_fieldnames,
                **kwargs,
            ).import_list(**kwargs)
        except RandomizationListAlreadyImported:
            pass
        return result

    @classmethod
    def verify_list(cls, **kwargs) -> List[str]:
        return cls.importer_cls.verifier_cls(
            assignment_map=cls.assignment_map,
            randomizationlist_path=cls.randomizationlist_path(),
            randomizer_model_cls=cls.model_cls(),
            randomizer_name=cls.name,
            **kwargs,
        ).messages
