from django.utils.text import camel_case_to_spaces


def model_name_as_attr(model):
    """Returns the a model name like PlotLogEntry as plot_log_entry."""
    return camel_case_to_spaces(
        model._meta.label.split('.')[1]).replace(' ', '_')
