import os

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from edc_registration.utils import get_registered_subject_model_cls

from edc_randomization.randomization_list_importer import (
    RandomizationListImporter,
    RandomizationListImportError,
)

from .constants import DEFAULT_ASSIGNMENT_MAP
from .randomization_list_verifier import RandomizationListVerifier

RANDOMIZED = "RANDOMIZED"

assignment_map = getattr(settings, "EDC_RANDOMIZATION_ASSIGNMENT_MAP", DEFAULT_ASSIGNMENT_MAP)


class RandomizationError(Exception):
    pass


class RandomizationListNotFound(Exception):
    pass


class RandomizationListNotLoaded(Exception):
    pass


class AlreadyRandomized(ValidationError):
    pass


class AllocationError(Exception):
    pass


class InvalidAllocation(Exception):
    pass


class InvalidAssignment(Exception):
    pass


class Randomizer:
    """Selects and uses the next available slot in model
    RandomizationList (cls.model) for this site. A slot is used
    when the subject identifier is not None.

    This is the default randomizer class and is registered with
    `site_randomizer` by default. To prevent registration set
    settings.EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False.
    """

    name = "default"
    model = "edc_randomization.randomizationlist"
    assignment_map = assignment_map
    filename = "randomization_list.csv"
    randomization_list_path = settings.EDC_RANDOMIZATION_LIST_PATH
    is_blinded_trial = True
    importer_cls = RandomizationListImporter

    def __init__(
        self, subject_identifier=None, report_datetime=None, site=None, user=None, **kwargs
    ):
        self._model_obj = None
        self._registered_subject = None
        self.subject_identifier = subject_identifier
        self.allocated_datetime = report_datetime
        self.site = site
        self.user = user
        if not os.path.exists(self.get_randomization_list_fullpath()):
            raise RandomizationListNotFound(
                "RandomizationListNotFound. "
                f"Got {self.get_randomization_list_fullpath()}. See {self}."
            )
        self.check_loaded()
        # force query, will raise if already randomized
        self.get_registered_subject()
        # will raise if already randomized
        self.randomize()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.name},{self.get_randomization_list_fullpath()})"
        )

    def __str__(self):
        return f"<{self.name} for file {self.get_randomization_list_fullpath()}>"

    def randomize(self):
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
        self.registered_subject.sid = self.model_obj.sid
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

    @classmethod
    def model_cls(cls, apps=None):
        return (apps or django_apps).get_model(cls.model)

    @classmethod
    def get_randomization_list_fullpath(cls):
        return os.path.expanduser(os.path.join(cls.randomization_list_path, cls.filename))

    @classmethod
    def get_assignment(cls, row):
        """Returns assignment (text) after checking validity."""
        assignment = row["assignment"]
        if assignment not in cls.assignment_map:
            raise InvalidAssignment(
                f"Invalid assignment. Expected one of {list(cls.assignment_map.keys())}. "
                f"Got `{assignment}`. "
                f"See randomizer `{cls.name}` {repr(cls)}. "
            )
        return assignment

    @classmethod
    def get_allocation(cls, row):
        """Returns an integer allocation for the given
        assignment or raises.
        """
        assignment = cls.get_assignment(row)
        return cls.assignment_map.get(assignment)

    @property
    def sid(self):
        """Returns the SID."""
        return self.model_obj.sid

    @classmethod
    def check_loaded(cls):
        try:
            cls.import_list(overwrite=False)
        except RandomizationListImportError:
            pass
        if cls.model_cls().objects.all().count() == 0:
            raise RandomizationListNotLoaded(
                "Randomization list has not been loaded. " "Run the management command."
            )

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

    @property
    def extra_model_obj_options(self):
        """Returns a dict of extra key/value pair for filtering the
        "rando" model.
        """
        return {}

    def get_registered_subject(self):
        return self.registered_subject

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
    def get_extra_list_display(cls):
        """Returns a list of tuples of (pos, field name) for ModelAdmin."""
        return []

    @classmethod
    def get_extra_list_filter(cls):
        """Returns a list of tuples of (pos, field name) for ModelAdmin."""
        return cls.get_extra_list_display()

    @classmethod
    def verify_list(cls):
        randomization_list_verifier = RandomizationListVerifier(randomizer_name=cls.name)
        return randomization_list_verifier.messages

    @classmethod
    def import_list(cls, **kwargs):
        importer = cls.importer_cls(randomizer_cls=cls, **kwargs)
        importer.import_list()
