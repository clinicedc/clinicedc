import csv

from django.apps import apps as django_apps


app_config = django_apps.get_app_config("edc_pharma")


class Holidays:

    path = app_config.holiday_csv_path

    def __init__(self, country=None, path=None):
        self.holidays = {}
        self.country = country
        self.path = path or self.path
        with open(self.path, "r") as f:
            reader = csv.DictReader(f, fieldnames=["local_date", "label", "country"])
            for row in reader:
                if row["country"] == self.country:
                    self.holidays.update({row["local_date"]: row["label"]})

    def __repr__(self):
        return f"{self.__class__.__name__}(country={self.country}, path={self.path})"

    def is_holiday(self, local_date=None):
        return str(local_date) in self.holidays
