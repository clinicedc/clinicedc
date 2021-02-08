#!/usr/bin/env python

"""
Generate a dummy randomization list.

This trial is randomized by site so all assignments are
the same within a site. Use this util to generate a dummy
randomization_list.csv for import into the RandomizationList
model. Patient registration always refers to and updates the
RandomizationList model.

Usage:
    python generate_randomization_list.py

    or

    python generate_randomization_list.py tests/site_assignments.csv


"""
import csv
import os
import sys

import django
from django.conf import settings
from edc_sites import get_site_id

# from inte_sites.sites import all_sites


def main(
    all_sites=None,
    country=None,
    site_name=None,
    assignment=None,
    slots=None,
    write_header=None,
    filename=None,
    assignment_map=None,
):
    """
    Adds slots to  a dummy `randomisation` list file where all assignments are the same
    for each slot.
    """
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
            sid = str(j).zfill(len(slots))
            writer.writerow(
                dict(
                    sid=f"{site_id}{sid}",
                    assignment=assignment,
                    site_name=site_name,
                    country=country,
                )
            )

    print(f"(*) Added {slots} slots for {site_name}.")


# if __name__ == "__main__":
#
#     # point the settings module to a bare-bones settings file.
#     settings_module = os.environ.setdefault(
#         "DJANGO_SETTINGS_MODULE", "inte_edc.settings.minimal"
#     )
#     if not settings_module:
#         raise EnvironmentError("`DJANGO_SETTINGS_MODULE` not set.")
#     django.setup()
#
#     # get filename, raise if exists
#     try:
#         etc_dir = os.path.expanduser(sys.argv[1])
#     except IndexError:
#         etc_dir = settings.ETC_DIR
#     randomization_list_file = os.path.join(etc_dir, "randomization_list.csv")
#     if os.path.exists(randomization_list_file):
#         raise FileExistsError(randomization_list_file)
#
#     with open(os.path.join(etc_dir, "site_assignments.csv"), newline="") as f:
#         reader = csv.DictReader(f)
#         for i, row in enumerate(reader):
#             main(
#                 country=row["country"],
#                 site_name=row["site_name"],
#                 assignment=row["assignment"],
#                 slots=row["slots"],
#                 filename=randomization_list_file,
#                 write_header=True if i == 0 else False,
#             )
#     # print the path
#     print(f"Done. Created {randomization_list_file}")
