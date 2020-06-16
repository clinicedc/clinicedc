import os

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from edc_registration.utils import get_registered_subject_model

from .constants import DEFAULT_ASSIGNMENT_MAP
from .randomization_list_verifier import RandomizationListVerifier

RANDOMIZED = "RANDOMIZED"

assignment_map = getattr(
    settings, "EDC_RANDOMIZATION_ASSIGNMENT_MAP", DEFAULT_ASSIGNMENT_MAP
)


class RandomizationError(Exception):
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
    is_blinded_trial = True

    def __init__(
        self, subject_identifier=None, report_datetime=None, site=None, user=None
    ):
        self._model_obj = None
        self._registered_subject = None
        self.subject_identifier = subject_identifier
        self.allocated_datetime = report_datetime
        self.site = site
        self.user = user
        self.check_loaded()
        # force query, will raise if already randomized
        self.registered_subject
        # will raise if already randomized
        self.randomize()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name},{self.get_randomization_list_path()})"

    def __str__(self):
        return f"<{self.name} for file {self.get_randomization_list_path()}>"

    @classmethod
    def model_cls(cls, apps=None):
        return (apps or django_apps).get_model(cls.model)

    @classmethod
    def get_randomization_list_path(cls):
        return os.path.join(settings.EDC_RANDOMIZATION_LIST_PATH, cls.filename)

    @classmethod
    def get_assignment(cls, row):
        """Returns assignment (text) after checking validity.
        """
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
        """Returns the SID.
        """
        return self.model_obj.sid

    def check_loaded(self):
        if self.model_cls().objects.all().count() == 0:
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
                obj = self.model_cls().objects.get(
                    subject_identifier=self.subject_identifier
                )
            except ObjectDoesNotExist:
                self._model_obj = (
                    self.model_cls()
                    .objects.filter(
                        subject_identifier__isnull=True, site_name=self.site.name
                    )
                    .order_by("sid")
                    .first()
                )
                if not self._model_obj:
                    raise AllocationError(
                        "Randomization failed. No additional SIDs available for "
                        f"site '{self.site.name}'."
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

    def randomize(self):
        if any(
            [
                not self.subject_identifier,
                not self.allocated_datetime,
                not self.user,
                not self.site,
            ]
        ):
            dct = dict(
                subject_identifier=self.subject_identifier,
                allocated_datetime=self.allocated_datetime,
                user=self.user,
                site=self.site,
            )
            raise RandomizationError(
                f"Randomization failed. Insufficient data. Got {dct}."
            )
        self.model_obj.subject_identifier = self.subject_identifier
        self.model_obj.allocated = True
        self.model_obj.allocated_datetime = self.allocated_datetime
        self.model_obj.allocated_user = self.user
        self.model_obj.allocated_site = self.site
        self.model_obj.save()
        # requery
        self._model_obj = self.model_cls().objects.get(
            subject_identifier=self.subject_identifier,
            allocated=True,
            allocated_datetime=self.allocated_datetime,
        )
        self.registered_subject.sid = self.model_obj.sid
        self.registered_subject.randomization_datetime = (
            self.model_obj.allocated_datetime
        )
        self.registered_subject.registration_status = RANDOMIZED
        self.registered_subject.randomization_list_model = (
            self.model_obj._meta.label_lower
        )
        self.registered_subject.save()
        # requery
        self._registered_subject = get_registered_subject_model().objects.get(
            subject_identifier=self.subject_identifier, sid=self.model_obj.sid
        )

    @property
    def registered_subject(self):
        """Returns an instance of the registered subject model.
        """
        if not self._registered_subject:
            try:
                self._registered_subject = get_registered_subject_model().objects.get(
                    subject_identifier=self.subject_identifier, sid__isnull=True
                )
            except ObjectDoesNotExist:
                try:
                    obj = get_registered_subject_model().objects.get(
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
                        code=get_registered_subject_model()._meta.label_lower,
                    )
        return self._registered_subject

    @classmethod
    def verify_list(cls):
        randomization_list_verifier = RandomizationListVerifier(
            randomizer_name=cls.name
        )
        return randomization_list_verifier.messages
