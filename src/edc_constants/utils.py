from clinicedc_constants import QUESTION_RETIRED

def append_question_retired_choice(choices) -> tuple[tuple[str, str], ...]:
    choices = list(choices)
    choices.append((QUESTION_RETIRED, QUESTION_RETIRED))
    return tuple(choices)
