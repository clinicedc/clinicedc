import factory

from django.utils import timezone

from ..models import Holiday


class HolidayFactory(factory.DjangoModelFactory):

    class Meta:
        model = Holiday

    holiday_name = "public holiday"
    holiday_date = timezone.now().date()
