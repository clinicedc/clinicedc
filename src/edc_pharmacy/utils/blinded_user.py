from edc_randomization.auth_objects import RANDO_UNBLINDED
from edc_randomization.blinding import user_is_blinded


def blinded_user(request) -> bool:
    return user_is_blinded(request.user.username) or (
        not user_is_blinded(request.user.username)
        and RANDO_UNBLINDED not in [g.name for g in request.user.groups.all()]
    )


__all__ = ["blinded_user"]
