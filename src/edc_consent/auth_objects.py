from .utils import get_consent_model_name, get_reconsent_model_name

consent_codenames = []
models = [get_consent_model_name()]
if get_reconsent_model_name():
    models.append(get_reconsent_model_name())
for model in models:
    for action in ["view_", "add_", "change_", "delete_", "view_historical"]:
        consent_codenames.append(f".{action}".join(model.split(".")))

navbar_codenames = [
    "edc_consent.nav_consent",
]

navbar_tuples = []
for codename in navbar_codenames:
    navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))

consent_codenames.extend(navbar_codenames)
consent_codenames.sort()
