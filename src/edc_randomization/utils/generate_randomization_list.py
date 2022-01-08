#!/usr/bin/env python

"""
Generate a dummy randomization list.

This trial is randomized by site so all assignments are
the same within a site. Use this util to generate a dummy
randomization_list.csv for import into the RandomizationList
model. Patient registration always refers to and updates the
RandomizationList model.

"""

import csv
from typing import Optional

from edc_sites import get_site_id


def generate_randomization_list(
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
    Adds slots to  a dummy `randomisation` list file where all assignments are the same
    for each slot.
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
