from __future__ import annotations

from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import CHOL, DM, HIV, HTN, NO
from edc_dx import get_diagnosis_labels

default_prompts = {
    HIV.lower(): "Has the patient ever tested <U>positive</U> for HIV infection?",
    DM: "Has the patient ever been diagnosed with DIABETES?",
    HTN: "Has the patient ever been diagnosed with HYPERTENSION?",
    CHOL: "Has the patient ever been diagnosed with HIGH CHOLESTEROL?",
}


def baseline_review_model_mixin_factory(prompts: dict[str, str] | None = None):
    prompts = prompts or default_prompts

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {}
    for cond, label in get_diagnosis_labels().items():
        opts.update(
            {
                f"{cond}_dx": models.CharField(
                    verbose_name=prompts.get(cond),
                    max_length=15,
                    choices=YES_NO,
                ),
                f"{cond}_dx_at_screening": models.CharField(
                    verbose_name=f"Was a diagnosis of {label.upper()} reported at screening?",
                    max_length=15,
                    choices=YES_NO,
                ),
            }
        )

    opts.update(
        {
            "protocol_incident": models.CharField(
                verbose_name=(
                    "Do any of the above diagnosis differ from those reported at screening?"
                ),
                max_length=15,
                choices=YES_NO,
                default=NO,
            )
        }
    )
    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel
