from __future__ import annotations

from django.db import models
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import CHOL, DM, HIV, HTN, NOT_APPLICABLE
from edc_dx import get_diagnosis_labels

default_prompts = {
    HIV.lower(): "Since last seen, has the patient tested <U>positive</U> for HIV infection?",
    DM: "Since last seen, has the patient been diagnosed with Diabetes?",
    HTN: "Since last seen, has the patient been diagnosed with Hypertension?",
    CHOL: "Since last seen, has the patient been diagnosed with High Cholesterol?",
}


def followup_review_model_mixin_factory(prompts: dict[str, str] | None = None):
    prompts = prompts or default_prompts

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {}
    for dx in get_diagnosis_labels():
        opts.update(
            {
                f"{dx}_dx": models.CharField(
                    verbose_name=prompts.get(dx),
                    max_length=15,
                    choices=YES_NO_NA,
                    default=NOT_APPLICABLE,
                )
            }
        )

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel
