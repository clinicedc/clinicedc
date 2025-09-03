from .get_appointments import get_appointments


def get_next_appointments(**kwargs):
    """Returns a dataframe for the next appointment in the
    appointment schedule (first record where appt_status=NEW_APPT).

    To show appts where next appt is a future date:
        df = get_next_appointments()
        df[df.next_appt_datetime>=pd.to_datetime("today")]

    """
    df = get_appointments(**kwargs)
    df = (
        df.groupby(
            by=[
                "subject_identifier",
                "site_id",
                "next_visit_code",
                "next_appt_datetime",
            ]
        )
        .size()
        .to_frame()
        .reset_index()
    )
    df = df[["subject_identifier", "site_id", "next_visit_code", "next_appt_datetime"]]
    return df
