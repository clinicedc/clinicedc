def post_migrate_update_notifications(sender=None, **kwargs):
    from .site_notifications import site_notifications  # noqa: PLC0415

    site_notifications.update_notification_list(verbose=True)
    site_notifications.create_mailing_lists(verbose=True)
