from django.apps import apps as django_apps


def get_rxrefill_model_cls():
    return django_apps.get_model("edc_pharmacy.rxrefill")


def get_rx_model_cls():
    return django_apps.get_model("edc_pharmacy.rx")
