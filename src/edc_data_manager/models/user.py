from django.contrib.auth.models import User as BaseUser


class DataManagerUser(BaseUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    class Meta:
        proxy = True
        default_permissions = ("view", "export")
        verbose_name = "Data Manager User"
        verbose_name_plural = "Data Manager Users"


class QueryUser(BaseUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    class Meta:
        proxy = True
        default_permissions = ("view", "export")
        verbose_name = "Data Query User"
        verbose_name_plural = "Data Query Users"
