import random

random.seed(3897538743783)


def get_random_code(model_cls, length: int, tries: int | None = None) -> str:
    random_code = 0
    x = 0
    tries = tries or 1000
    while x < tries:
        random_code = str(
            "".join(
                [
                    random.choice("ABCDEFGHJKMNPQRTUVWXYZ2346789")  # nosec B311
                    for _ in range(0, length)
                ]
            )
        )
        if not model_cls.objects.filter(code=random_code).exists():
            break
        x += 1
        if x == tries:
            raise StopIteration()
    return random_code


__all__ = ["get_random_code"]
