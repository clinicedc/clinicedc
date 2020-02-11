import csv
import os
import uuid

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site


class AllocationError(Exception):
    pass


def get_assignment(allocation):
    if allocation == 1:
        return "placebo"
    elif allocation == 2:
        return "active"
    else:
        raise AllocationError(f"Invalid allocation. Got {allocation}")


def get_allocation(assignment):
    if assignment == "placebo":
        return "1"
    elif assignment == "active":
        return "2"
    else:
        raise AllocationError(f"Invalid assignment. Got {assignment}")


def new_rows(allocations=None, site_name=None, allocation_map=None):
    rows = []
    for index, allocation in enumerate(allocations, 1):
        rows.append(
            dict(
                sid=index,
                allocation=str(allocation),
                assignment=allocation_map[allocation],
                site_name=site_name,
                site_id=Site.objects.get(name=site_name).id,
            )
        )
    return rows


def import_allocations(
    model=None, allocations=None, site_name=None, allocation_map=None, dry_run=None
):
    rows = new_rows(
        allocations=allocations, site_name=site_name, allocation_map=allocation_map
    )
    randomizationlist_model_cls = django_apps.get_model(model)
    last_sid = randomizationlist_model_cls.objects.all().order_by("sid").last().sid
    objs = []
    for row in rows:
        row = {k: v.strip() for k, v in row.items()}
        try:
            obj = randomizationlist_model_cls.objects.get(sid=last_sid + row["sid"])
        except ObjectDoesNotExist:
            obj = randomizationlist_model_cls(
                id=uuid.uuid4(),
                sid=last_sid + row["sid"],
                assignment=row["assignment"],
                site_name=row["site"],
                allocation=get_allocation(row["assignment"]),
            )
            objs.append(obj)
    if dry_run:
        print(objs)
    else:
        randomizationlist_model_cls.objects.bulk_create(objs)


def import_additional_sids_from_file(
    filename=None, model=None, allocations=None, dry_run=None
):
    objs = []
    filename = filename or "~/rando_additional.txt"
    randomizationlist_model_cls = django_apps.get_model(model)
    last_sid = randomizationlist_model_cls.objects.all().order_by("sid").last().sid

    with open(os.path.join(os.path.expanduser(filename)), "r") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader, 1):
            row = {k: v.strip() for k, v in row.items()}
            try:
                obj = randomizationlist_model_cls.objects.get(sid=last_sid + index)
            except ObjectDoesNotExist:
                obj = randomizationlist_model_cls(
                    id=uuid.uuid4(),
                    sid=last_sid + index,
                    assignment=row["assignment"],
                    site_name=row["site"],
                    allocation=get_allocation(row["assignment"]),
                )
                objs.append(obj)
    if dry_run:
        print(objs)
    else:
        randomizationlist_model_cls.objects.bulk_create(objs)
