import re


class CheckDigit(object):

    """ Create or validate a check digit"""

    def calculate(self, number, modulus=7):

        if isinstance(number, basestring):
            number = re.search(r'\d+', number).group(0)
            try:
                number = int(number)
            except:
                raise TypeError('Number must be an integer or a string containing numbers '
                                'that will implicitly convert to an integer. Got {0}'.format(number))
        # using the integer segment, calculate the check digit
        check_digit = number % modulus

        # pad the check digit if required based on the modulus
        if modulus > 100 and modulus <= 1000:
            if check_digit < 10:
                check_digit = "00{0}".format(check_digit)
            if check_digit >= 10 and check_digit < 100:
                check_digit = "0{0}".format(check_digit)

        if modulus > 10 and modulus <= 100:
            if check_digit < 10:
                check_digit = "0{0}".format(check_digit)

        return check_digit
