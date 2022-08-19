from typing import Dict

RANDOMIZED = "RANDOMIZED"

ACTIVE = "active"
ACTIVE_NAME = "Active: "
PLACEBO = "placebo"
PLACEBO_NAME = "Placebo: "
DEFAULT = "default"
DEFAULT_ASSIGNMENT_MAP: Dict[str, int] = {ACTIVE: 1, PLACEBO: 2}
DEFAULT_ASSIGNMENT_DESCRIPTION_MAP: Dict[str, str] = {ACTIVE: "Active", PLACEBO: "Placebo"}
EXPORT_RANDO = "EXPORT_RANDO"
CONTROL = "control"
INTERVENTION = "intervention"
