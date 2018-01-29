

class LuhnMixin:

    def calculate_checkdigit(self, identifier):
        check_digit = self._luhn_checksum(
            int(''.join(map(str, self._digits_of(identifier)))) * 10)
        check_digit = check_digit if check_digit == 0 else 10 - check_digit
        return str(check_digit)

    def _digits_of(self, n):
        return [int(d) for d in str(n)]

    def _luhn_checksum(self, identifier):
        digits = self._digits_of(identifier)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(self._digits_of(d * 2))
        return checksum % 10


class LuhnOrdMixin(LuhnMixin):
    """Accepts alpha/numeric but is not standard."""

    def _digits_of(self, n):
        return [ord(d) for d in str(n)]
