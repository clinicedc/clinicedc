import csv
import os
from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from edc_pdutils.model_to_dataframe import ModelToDataframe
from edc_sites import get_site_id
from edc_utils import get_utcnow

from .site_randomizers import site_randomizers


class RandomizationListExporterError(Exception):
    pass


class SubjectNotRandomization(Exception):
    pass


def get_assignment_for_subject(subject_identifier: str, randomizer_name: str = None) -> str:
    """Returns the assignment for a randomized subject.

    Calling this method before a subject is randomized will
    raise a SubjectNotRandomization error.
    """
    obj = get_object_for_subject(subject_identifier, randomizer_name)
    return obj.assignment


def get_assignment_description_for_subject(
    subject_identifier: str, randomizer_name: str = None
) -> str:
    """Returns the assignment description for a randomized subject.

    Calling this method before a subject is randomized will
    raise a SubjectNotRandomization error.
    """
    randomizer_cls = site_randomizers.get(randomizer_name)
    return randomizer_cls.assignment_description_map.get(
        get_assignment_for_subject(subject_identifier, randomizer_name)
    )


def get_object_for_subject(subject_identifier: str, randomizer_name: str = None) -> Any:
    """Returns a randomization list model instance or raises
    for the given subject.

    Calling this method before a subject is randomized will
    raise a SubjectNotRandomization error.
    """
    randomizer_cls = site_randomizers.get(randomizer_name)
    try:
        obj = randomizer_cls.model_cls().objects.get(
            subject_identifier=subject_identifier,
            randomizer_name=randomizer_name,
            allocated=True,
            allocated_datetime__isnull=False,
        )
    except ObjectDoesNotExist:
        raise SubjectNotRandomization(
            f"Subject not randomized. Randomizer name is `{randomizer_name}`. "
            f"Got {subject_identifier}."
        )
    return obj


def generate_fake_randomization_list(
    all_sites=None,
    country=None,
    site_name=None,
    assignment: Optional[list] = None,
    slots: Optional[int] = None,
    write_header: Optional[bool] = None,
    filename=None,
    assignment_map=None,
):
    """
    Generate a dummy randomization list.

    This trial is randomized by site so all assignments are
    the same within a site. Use this util to generate a dummy
    randomization_list.csv for import into the RandomizationList
    model. Patient registration always refers to and updates the
    RandomizationList model.

    Add slots to a dummy `randomization` list file where all
    assignments are the same for each slot.
    """
    slots = slots or 10
    assignment_map = assignment_map or ["intervention", "control"]
    if assignment not in assignment_map:
        raise ValueError(f"Invalid assignment. Got {assignment}")

    # get site ID and write the file
    site_id = get_site_id(site_name, sites=all_sites[country])
    with open(filename, "a+", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sid", "assignment", "site_name", "country"])
        if write_header:
            writer.writeheader()
        for j in range(1, int(slots)):
            sid = str(j).zfill(len(str(slots)))
            writer.writerow(
                dict(
                    sid=f"{site_id}{sid}",
                    assignment=assignment,
                    site_name=site_name,
                    country=country,
                )
            )

    print(f"(*) Added {slots} slots for {site_name}.")


def export_randomization_list(
    randomizer_name: str, path: Optional[str] = None, username: Optional[str] = None
):
    randomizer_cls = site_randomizers.get(randomizer_name)

    try:
        user = get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
        raise RandomizationListExporterError(f"User `{username}` does not exist")
    if not user.has_perm(randomizer_cls.model_cls()._meta.label_lower.replace(".", ".view_")):
        raise RandomizationListExporterError(
            f"User `{username}` does not have "
            f"permission to view '{randomizer_cls.model_cls()._meta.label_lower}'"
        )
    path = path or settings.EXPORT_FOLDER
    timestamp = get_utcnow().strftime("%Y%m%d%H%M")
    filename = os.path.expanduser(
        f"~/{settings.APP_NAME}_{randomizer_cls.name}_"
        f"randomizationlist_exported_{timestamp}.csv"
    )
    filename = os.path.join(path, filename)

    df = ModelToDataframe(
        model=randomizer_cls.model_cls()._meta.label_lower, decrypt=True, drop_sys_columns=True
    )
    opts = dict(
        path_or_buf=filename,
        encoding="utf-8",
        index=0,
        sep="|",
    )
    df.dataframe.to_csv(**opts)
    print(filename)
    return filename
