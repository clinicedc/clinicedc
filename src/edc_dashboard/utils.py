from django.conf import settings


def insert_bootstrap_version(**template_data):
    """Insert bootstrap version.
    """

    try:
        bootstrap_version = settings.EDC_BOOTSTRAP
    except AttributeError:
        bootstrap_version = 3
    for key, value in template_data.items():
        if '/bootstrap' not in value:
            value = value.split('/')
            value.insert(1, f'bootstrap{bootstrap_version}')
            value = '/'.join(value)
        template_data.update({key: value})
    return template_data
