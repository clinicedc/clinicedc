class SubjectResolution:
    """Result of attempting to resolve a name_id to a registered
    subject.
    """

    __slots__ = (
        "match_category",
        "match_comment",
        "resolved",
        "screening_identifier",
        "subject_identifier",
    )

    def __init__(
        self,
        subject_identifier: str = "",
        screening_identifier: str = "",
        *,
        resolved: bool = False,
    ) -> None:
        self.subject_identifier = subject_identifier
        self.screening_identifier = screening_identifier
        self.resolved = resolved
        self.match_category: str = ""
        self.match_comment: str = ""
