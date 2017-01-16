from django.utils.text import camel_case_to_spaces


def model_name_as_attr(model_object):
    """Returns the a model name like PlotLogEntry as plot_log_entry."""
    try:
        name = model_object._meta.label.split('.')[1]
    except AttributeError:
        name = model_object.wrapped_object._meta.label.split('.')[1]
    return camel_case_to_spaces(name).replace(' ', '_')
