from django.apps import apps as django_apps


def get_data_queries(subject_identifier=None, model=None, status=None, **kwargs):
    """Convenience func to return a data_query QuerySet."""
    model_cls = django_apps.get_model("edc_data_manager.dataquery")
    opts = {}
    if subject_identifier:
        opts.update(subject_identifier=subject_identifier)
    if model:
        opts.update(data_dictionaries__model=model)
    if status:
        opts.update(status=status)
    opts.update(**kwargs)
    return model_cls.objects.filter(**opts)
