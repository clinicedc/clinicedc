from django.conf import settings

GLUCOSE_HIGH_READING = getattr(settings, "EDC_GLUCOSE_HIGH_READING", 9999.99)
