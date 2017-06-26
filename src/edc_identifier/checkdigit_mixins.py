from .exceptions import CheckDigitError


class BaseCheckDigit:

    def is_valid_checkdigit(self, identifier, checkdigit):
        try:
            if int(self.calculate_checkdigit(identifier)) != int(checkdigit):
                raise CheckDigitError(
                    'Invalid checkdigit. Got {} from base identifier {}'.format(
                        checkdigit, identifier))
            return True
        except CheckDigitError:
            return False


class LuhnMixin(BaseCheckDigit):

    def calculate_checkdigit(self, identifier):
        return str(self._calculate_luhn(identifier))

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

    def _calculate_luhn(self, identifier):
        check_digit = self._luhn_checksum(
            int(''.join(map(str, self._digits_of(identifier)))) * 10)
        return check_digit if check_digit == 0 else 10 - check_digit


class LuhnOrdMixin(LuhnMixin):
    """Accepts alpha/numeric but is not standard."""

    def _digits_of(self, n):
        return [ord(d) for d in str(n)]


class ModulusMixin(BaseCheckDigit):

    modulus = 13

    @property
    def length(self):
        return len(str((self.modulus - 1) % self.modulus))

    def calculate_checkdigit(self, identifier):
        identifier = identifier.replace(self.separator or '', '')
        checkdigit = int(identifier) % self.modulus
        frmt = '{{0:0{}d}}'.format(self.length)
        return frmt.format(checkdigit)
