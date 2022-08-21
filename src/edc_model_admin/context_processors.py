from django.conf import settings
from edc_constants.constants import LIVE, TEST
from edc_protocol import Protocol


def admin_theme(request) -> dict:
    dct = {
        "LIVE_SYSTEM": getattr(settings, "LIVE_SYSTEM", False),
        "DEBUG": getattr(settings, "DEBUG", False),
        "LIVE": LIVE,
        "TEST": TEST,
        "project_name": Protocol().project_name,
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
