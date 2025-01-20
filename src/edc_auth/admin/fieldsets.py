from django.utils.html import format_html
from django.utils.safestring import mark_safe

user_profile_fieldsets = (
    (
        "Profile details",
        (
            {
                "fields": (
                    "job_title",
                    "alternate_email",
                    "mobile",
                )
            }
        ),
    ),
    (
        "Roles",
        ({"fields": ("roles",)}),
    ),
    (
        "Multisite viewer status",
        (
            {
                "description": format_html(
                    "{}",
                    mark_safe(
                        "Multisite viewer status designates the user with view only access to "
                        "data from the current site and all other sites the user has "
                        "permission to access (see Sites below). <BR>"
                        "<BR><B>Note:</B> <i>This status is restricted to accounts that do "
                        "not have add/change/delete permissions to other objects.</i><br>"
                        "<BR>Allowing `multisite viewers` status is done in two steps. "
                        "<ol><li>Adjust the account permissions accordingly and save "
                        "this form <li>Re-open this form, select the option, "
                        "and save the form again.</ol>"
                    ),  # nosec B703 B308
                ),
                "fields": ("is_multisite_viewer",),
            }
        ),
    ),
    (
        "Sites",
        ({"fields": ("sites",)}),
    ),
    (
        "Email and SMS",
        (
            {
                "fields": (
                    "email_notifications",
                    "sms_notifications",
                )
            }
        ),
    ),
    (
        "Data export",
        ({"fields": ("export_format",)}),
    ),
    (
        "Printing profile",
        (
            {
                "fields": (
                    "clinic_label_printer",
                    "lab_label_printer",
                    "print_server",
                )
            }
        ),
    ),
)
