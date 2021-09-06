from django.contrib.auth.models import User as BaseUser


class UnblindingRequestorUser(BaseUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    class Meta:
        proxy = True
        default_permissions = ("view",)
        verbose_name = "Unblinding Requestor (User)"
        verbose_name_plural = "Unblinding Requestors (Users)"


class UnblindingReviewerUser(BaseUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    class Meta:
        proxy = True
        default_permissions = ("view",)
        verbose_name = "Unblinding Reviewer (User)"
        verbose_name_plural = "Unblinding Reviewers (Users)"
