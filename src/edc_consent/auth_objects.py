from .utils import get_consent_model_name, get_reconsent_model_name

consent_codenames = []
for model in [get_reconsent_model_name(), get_consent_model_name()]:
    for action in ["view_", "add_", "change_", "delete_", "view_historical"]:
        consent_codenames.append(f".{action}".join(model.split(".")))


consent_codenames.sort()
