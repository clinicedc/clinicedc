
class AliquotType:

    def __init__(self, name, alpha_code, numeric_code):
        self.derivatives = []
        self.name = name
        self.alpha_code = alpha_code
        self.numeric_code = numeric_code

    def __repr__(self):
        return '<AliquotType({}, {}, {})>'.format(self.name, self.alpha_code, self.numeric_code)

    def __str__(self):
        return '{} {} {}'.format(self.name, self.alpha_code, self.numeric_code)

    def add_derivative(self, aliquot_type):
        self.derivatives.append(aliquot_type)
