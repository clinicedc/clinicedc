

class DispenseProfile:

    """A container class for medication type.
    """

    def __init__(self, name=None, profile_type=None):
        self.name = name
        self.profile_type = profile_type
        self.medication_types = {}
        self.label = f'{self.name}.{self.profile_type}'

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def __str__(self):
        return self.name

    def add_medication_type(self, medication_type):
        """Adds a medication type instance to the profile.
        """
        self.medication_types.update({medication_type.name: medication_type})

    def get_medication_type(self, name=None):
        """ Returns a medication type instance using name.
        """
        return self.medication_types.get(name)
