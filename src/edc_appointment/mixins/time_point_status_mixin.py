from django.apps import apps as django_apps


class TimePointStatusMixin(object):

    def save(self, *args, **kwargs):
        """Raises a ValidationError if timepoint is closed."""
        using = kwargs.get('using')
        if self.id and not self.byass_time_point_status():
            self.check_time_point_status(self.visit.appointment, using=using)
        super(TimePointStatusMixin, self).save(*args, **kwargs)

    def byass_time_point_status(self):
        """Returns False by default but if overridden and set to return
        True, the TimePointStatus instance will not be checked in the save
        method.

        This does not effect the call from the ModelForm."""
        return False

    def check_time_point_status(self, appointment, exception_cls=None, using=None):
        """Checks the timepoint status and prevents edits to the model if
        time_point_status_status == closed."""
        TimePointStatus = django_apps.get_model('edc_appointment', 'TimePointStatus')
        exception_cls = exception_cls or ValidationError
        try:
            try:
                time_point_status = TimePointStatus.objects.using(using).get(appointment=self.visit.appointment)
            except AttributeError:
                time_point_status = TimePointStatus.objects.using(using).get(appointment=self.appointment)
            if time_point_status.status == CLOSED:
                raise exception_cls(
                    'Data for this timepoint / appointment is closed. See TimePointStatus.')
        except TimePointStatus.DoesNotExist:
            pass  # will be created in signal
