from .exceptions import CheckDigitError


class BaseCheckDigitMixin(object):

    def is_valid_checkdigit(self, identifier, checkdigit):
        try:
            if int(self.calculate_checkdigit(identifier)) != int(checkdigit):
                raise CheckDigitError(
                    'Invalid checkdigit. Got {} from base identifier {}'.format(
                        checkdigit, identifier))
            return True
        except CheckDigitError:
            return False


class LuhnMixin(BaseCheckDigitMixin):

    def calculate_checkdigit(self, identifier):
        return str(self.calculate_luhn(identifier))

    def digits_of(self, n):
        return [int(d) for d in str(n)]

    def luhn_checksum(self, identifier):
        digits = self.digits_of(identifier)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(self.digits_of(d * 2))
        return checksum % 10

    def calculate_luhn(self, identifier):
        check_digit = self.luhn_checksum(int(''.join(map(str, self.digits_of(identifier)))) * 10)
        return check_digit if check_digit == 0 else 10 - check_digit


class LuhnOrdMixin(LuhnMixin):
    """Accepts alpha/numeric but is not standard."""

    def digits_of(self, n):
        return [ord(d) for d in str(n)]


class ModulusMixin(BaseCheckDigitMixin):

    modulus = 13

    @property
    def length(self):
        return len(str((self.modulus - 1) % self.modulus))

    def calculate_checkdigit(self, identifier):
        identifier = identifier.replace(self.separator or '', '')
        checkdigit = int(identifier) % self.modulus
        frmt = '{{0:0{}d}}'.format(self.length)
        return frmt.format(checkdigit)
