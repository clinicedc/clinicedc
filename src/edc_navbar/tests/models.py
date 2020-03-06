from edc_model.models import BaseUuidModel, HistoricalRecords


class SubjectConsent(BaseUuidModel):
    history = HistoricalRecords()

    class Meta:
        pass


class SubjectReconsent(BaseUuidModel):
    history = HistoricalRecords()

    class Meta:
        pass


class SubjectVisit(BaseUuidModel):
    history = HistoricalRecords()

    class Meta:
        pass


class SubjectRequisition(BaseUuidModel):
    history = HistoricalRecords()

    class Meta:
        pass
