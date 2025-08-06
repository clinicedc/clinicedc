from edc_randomization.auth_objects import RANDO_UNBLINDED
from edc_randomization.blinding import user_is_blinded


def blinded_user(request) -> bool:
    if user_is_blinded(request.user.username) or (
        not user_is_blinded(request.user.username)
        and RANDO_UNBLINDED not in [g.name for g in request.user.groups.all()]
    ):
        # user is blinded
        return True
    # user is not blinded
    return False


__all__ = ["blinded_user"]
