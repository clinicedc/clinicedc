class RuleResult:
    def __init__(
        self,
        rule_object=None,
        subject_identifiers=None,
        rule_title=None,
        model_cls=None,
        visit_schedule=None,
        invalid_field_value=None,
    ):
        self.invalid_field_value = invalid_field_value
        self.model_cls = model_cls
        self.object = rule_object
        self.rule_title = rule_title
        self.subject_identifiers = subject_identifiers
        self.visit_schedule = visit_schedule

    def __repr__(self):
        return f"{self.__class__.__name__}()<{self.rule_title}, model={self.model_cls._meta.label_lower} rule_title={self.rule_title}>"

    def __str__(self):
        return f"model={self.model_cls._meta.label_lower} rule_title={self.rule_title}"
