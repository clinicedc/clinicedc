from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .modeladmin_mixins import ModelAdminSubjectDashboardMixin
from .model_wrappers import AppointmentModelWrapper, AppointmentModelWrapperError
from .model_wrappers import SubjectVisitModelWrapper

name = 'edc_subject_dashboard.middleware.DashboardMiddleware'
if name not in settings.MIDDLEWARE:
    raise ImproperlyConfigured(f'Missing middleware. Expected {name}.')
