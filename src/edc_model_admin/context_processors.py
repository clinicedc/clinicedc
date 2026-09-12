from clinicedc_constants import LIVE, TEST
from django.conf import settings

from edc_protocol.trial_settings import trial_settings


def admin_theme(request) -> dict:
    dct = {
        "LIVE_SYSTEM": getattr(settings, "LIVE_SYSTEM", False),
        "DEBUG": getattr(settings, "DEBUG", False),
        "LIVE": LIVE,
        "TEST": TEST,
        "project_name": trial_settings.project_name,
    }
    if theme := getattr(settings, "EDC_MODEL_ADMIN_CSS_THEME", None):
        dct.update(
            {
                "edc_model_admin_css_theme_path": (
                    [
                        "edc_model_admin/admin/css/edc_model_admin.css",
                        f"edc_model_admin/admin/css/themes/{theme.lower()}.css",
                    ]
                )
            }
        )
    return dct
