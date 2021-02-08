from warnings import warn

import pandas as pd

from ..model_to_dataframe import SubjectModelToDataframe


def missing_subject_identifiers(
    self, model=None, subject_identifiers=None, remove_uuids=None, verbose=None
):
    """Returns a series of subject_identifiers not in model.

    For example:
        missing_subject_identifiers(
            model='edc_registration.registeredsubject',
            subject_identifiers=[a list of subject identifiers])
    """
    # convert list of subject identifiers to a dataframe
    df_subject_identifiers = pd.DataFrame(subject_identifiers, columns=["subject_identifier"])
    df_subject_identifiers["identifier"] = df_subject_identifiers["subject_identifier"]
    df_subject_identifiers = df_subject_identifiers.set_index("subject_identifier")
    if verbose:
        df_subject_identifiers.head()

    # load model into dataframe
    df_subject = SubjectModelToDataframe(model=model).dataframe
    # drop duplicates
    df_subject = df_subject.drop_duplicates()
    # remove subject identifier as UUID
    if remove_uuids:
        df_subject = df_subject[df_subject["subject_identifier"].str.len() != 32]
    # set index to subject_identifier
    df_subject = df_subject.set_index("subject_identifier")
    # filter df of subject identifiers to leave only those not in model
    df_missing = df_subject_identifiers[
        -df_subject_identifiers["identifier"].isin(df_subject.index)
    ]

    if len(df_missing.index) > 0 and verbose:
        warn(
            f'There are {len(df_missing["identifier"])} subject identifiers '
            f"missing from {model}."
        )
    return df_missing["identifier"]
