from django.db import models
from edc_model.models import BaseUuidModel
from django.contrib.auth import get_user_model
from edc_utils.date import get_utcnow

User = get_user_model()


class DataQuery(BaseUuidModel):

    query_datetime = models.DateTimeField(default=get_utcnow)

    subject_identifier = models.CharField(max_length=25)

    question = models.CharField(max_length=25, null=True)

    query = models.TextField()

    users = models.ManyToManyField(User)

    response = models.TextField()


class Question(BaseUuidModel):

    visit_code = models.CharField(max_length=25)

    form_name = models.CharField(max_length=50)

    number = models.IntegerField()

    prompt = models.CharField(max_length=250)

    field_name = models.CharField(max_length=50)
