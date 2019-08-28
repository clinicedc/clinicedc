from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError

RANDOMIZED = "RANDOMIZED"


class RandomizationError(Exception):
    pass


class RandomizationListError(Exception):
    pass


class AlreadyRandomized(ValidationError):
    pass


class AllocationError(Exception):
    pass


class Randomizer:

    model = None  # "ambition_rando.randomizationlist"
    registered_subject_model = "edc_registration.registeredsubject"

    def __init__(
        self, subject_identifier=None, report_datetime=None, site=None, user=None
    ):
        self._model_obj = None
        self._registered_subject = None
        self.subject_identifier = subject_identifier
        self.allocated_datetime = report_datetime
        self.site = site
        self.user = user
        self.model_cls = django_apps.get_model(self.model)
        self.check_loaded()
        # force query, will raise if already randomized
        self.registered_subject
        # will raise if already randomized
        self.randomize()

    @property
    def sid(self):
        """Returns the SID.
        """
        return self.model_obj.sid

    def check_loaded(self):
        if self.model_cls.objects.all().count() == 0:
            raise RandomizationListError(
                f"Randomization list has not been loaded. "
                f"Run the management command."
            )

    @property
    def model_obj(self):
        """Returns a "rando" model instance by selecting
        the next available SID.
        """
        if not self._model_obj:
            try:
                obj = self.model_cls.objects.get(
                    subject_identifier=self.subject_identifier
                )
            except ObjectDoesNotExist:
                self._model_obj = (
                    self.model_cls.objects.filter(
                        subject_identifier__isnull=True, site_name=self.site.name
                    )
                    .order_by("sid")
                    .first()
                )
                if not self._model_obj:
                    raise AllocationError(
                        f"Randomization failed. No additional SIDs available for "
                        f"site '{self.site.name}'."
                    )
            else:
                raise AlreadyRandomized(
                    f"Subject already randomized. "
                    f"Got {obj.subject_identifier} SID={obj.sid}. "
                    f"Something is wrong. Are registered_subject and "
                    f"{self.model} out of sync?.",
                    code=self.model,
                )
        return self._model_obj

    def randomize(self):
        self.model_obj.subject_identifier = self.subject_identifier
        self.model_obj.allocated = True
        self.model_obj.allocated_datetime = self.allocated_datetime
        self.model_obj.allocated_user = self.user
        self.model_obj.allocated_site = self.site
        self.model_obj.save()
        # requery
        self._model_obj = self.model_cls.objects.get(
            subject_identifier=self.subject_identifier,
            allocated=True,
            allocated_datetime=self.allocated_datetime,
        )
        self.registered_subject.sid = self.model_obj.sid
        self.registered_subject.randomization_datetime = (
            self.model_obj.allocated_datetime
        )
        self.registered_subject.registration_status = RANDOMIZED
        self.registered_subject.save()
        # requery
        self._registered_subject = self.registered_subject_model_cls.objects.get(
            subject_identifier=self.subject_identifier, sid=self.model_obj.sid
        )

    @property
    def registered_subject_model_cls(self):
        """Returns the registered subject model class.
        """
        return django_apps.get_model(self.registered_subject_model)

    @property
    def registered_subject(self):
        """Returns an instance of the registered subject model.
        """
        if not self._registered_subject:
            try:
                self._registered_subject = self.registered_subject_model_cls.objects.get(
                    subject_identifier=self.subject_identifier, sid__isnull=True
                )
            except ObjectDoesNotExist:
                try:
                    obj = self.registered_subject_model_cls.objects.get(
                        subject_identifier=self.subject_identifier
                    )
                except ObjectDoesNotExist:
                    raise RandomizationError(
                        f"Subject does not exist. Got {self.subject_identifier}"
                    )
                else:
                    raise AlreadyRandomized(
                        f"Subject already randomized. See RegisteredSubject. "
                        f"Got {obj.subject_identifier} "
                        f"SID={obj.sid}",
                        code=self.registered_subject_model,
                    )
        return self._registered_subject
