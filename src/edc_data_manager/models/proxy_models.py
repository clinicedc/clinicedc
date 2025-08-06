from edc_form_runners.models import Issue as BaseIssue


class Issue(BaseIssue):
    class Meta:
        proxy = True
        verbose_name = "Form validation issue"
        verbose_name_plural = "Form validation issues"
