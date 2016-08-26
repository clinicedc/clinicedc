from edc_consent.exceptions import SiteConsentError, AlreadyRegistered


class SiteConsents:

    def __init__(self):
        self.registry = []
        self.check()

    def register(self, consent):
        for item in self.registry:
            if (item.valid_for_datetime(consent.start) and
                    item.valid_for_datetime(consent.end)):
                raise AlreadyRegistered('Consent already registered. Got {}'.format(str(consent)))
        self.check_version(consent)
        self.check_updates_version(consent)
        self.check_consent_period(consent)
        self.registry.append(consent)

    def reset_registry(self):
        self.registry = []

    def all(self):
        return sorted(self.registry, key=lambda x: x.version, reverse=False)

    def check(self):
        for consent in self.registry:
            self.check_updates_version(consent)
            self.check_consent_period(consent)

    def get_label_lower(self, model):
        try:
            label_lower = model._meta.label_lower
        except AttributeError:
            label_lower = model
        return label_lower

    def get_by_model(self, model=None):
        """Returns a list of consents configured with the given consent model."""
        consents = []
        label_lower = self.get_label_lower(model)
        for consent in self.registry:
            if consent.label_lower == label_lower:
                consents.append(consent)
        return consents

    def get_by_version(self, version, model):
        """Returns a list of consents of "version" configured with the given consent model."""
        consents = []
        label_lower = self.get_label_lower(model)
        for consent in self.registry:
            if consent.version == version and consent.label_lower == label_lower:
                consents.append(consent)
        return consents

    def get_all_by_version(self, version):
        """Returns a list of all consents using the given version regardless of the consent model."""
        consents = []
        for consent in self.registry:
            if consent.version == version:
                consents.append(consent)
        return consents

    def check_version(self, consent):
        if self.get_by_version(consent.version, '{}.{}'.format(consent.app_label, consent.model_name)):
            raise AlreadyRegistered(
                'Consent version {1} for \'{2}.{3}\' is already registered'.format(
                    consent.updates_version, consent.version,
                    consent.app_label, consent.model_name))

    def check_updates_version(self, consent):
        for version in consent.updates_version:
            if not self.get_by_version(version, consent.model):
                raise SiteConsentError(
                    'Consent version {1} cannot be an update to version(s) \'{0}\'. '
                    'Version(s) \'{0}\' not found in \'{2}\''.format(
                        consent.updates_version, consent.version,
                        consent.model._meta.label_lower))

    def check_consent_period(self, consent):
        registry = [ct for ct in self.registry if ct.slugify() != consent.slugify()]
        for ct in registry:
            if ct.app_label == consent.app_label and ct.model_name == consent.model_name:
                if (consent.start <= ct.start <= consent.end or
                        consent.start <= ct.end <= consent.end):
                    raise AlreadyRegistered(
                        'Consent period for version \'{0}\' overlaps with version \'{1}\'. '
                        'Got {2} to {3} overlaps with {4} to {5}.'.format(
                            ', '.join(consent.updates_version),
                            consent.version,
                            ct.start.strftime('%Y-%m-%d'),
                            ct.end.strftime('%Y-%m-%d'),
                            consent.start.strftime('%Y-%m-%d'),
                            consent.end.strftime('%Y-%m-%d')))

    def get_by_consent_datetime(self, consent_model, consent_datetime, exception_cls=None):
        return self.get_by_datetime(
            consent_model, consent_datetime, exception_cls=exception_cls)

    def get_by_report_datetime(self, consent_model, report_datetime, exception_cls=None):
        return self.get_by_datetime(
            consent_model, report_datetime, exception_cls=exception_cls)

    def get_by_datetime(self, consent_model, my_datetime, exception_cls=None):
        """Return consent object valid for the datetime."""
        exception_cls = exception_cls or SiteConsentError
        label_lower = self.get_label_lower(consent_model)
        consents = []
        for consent in self.registry:
            if consent.label_lower == label_lower and consent.valid_for_datetime(my_datetime):
                consents.append(consent)
        if not consents:
            raise exception_cls(
                'Cannot find a version for consent \'{}\' using date \'{}\'. '
                'Check consent in AppConfig.'.format(
                    label_lower,
                    my_datetime.isoformat()))
        if len(consents) > 1:
            raise exception_cls(
                'More than one consent version found for date. '
                'Check consents in AppConfig for {}'.format(label_lower))
        return consents[0]

site_consents = SiteConsents()
