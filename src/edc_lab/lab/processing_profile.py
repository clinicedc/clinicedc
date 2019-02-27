class ProcessingProfileInvalidDerivative(Exception):
    pass


class ProcessingProfileAlreadyAdded(Exception):
    pass


class Process:

    """A class to represent the resulting aliquot type and number of
    aliquots from the processing of a source aliquot.
    """

    def __init__(self, aliquot_type=None, aliquot_count=None):
        self.aliquot_type = aliquot_type
        self.aliquot_count = aliquot_count
        self.name = f"{self.aliquot_type.name} x {self.aliquot_count}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.aliquot_type}, {self.aliquot_count})"

    def __str__(self):
        return f"Process {self.name}"


class ProcessingProfile:

    """A container of process instances.

    Given a source aliquot, all processes in the profile
    will be "performed" to result in new aliquots of types
    and counts as per the processes.

    Only processes that produce aliquot types that match
    a `derivative` of the profiles aliquot type are accepted.
    """

    process_cls = Process

    def __init__(self, name=None, aliquot_type=None, verbose_name=None):
        self.aliquot_type = aliquot_type
        self.name = name
        self.processes = {}
        self.verbose_name = verbose_name or " ".join(name.split("_")).title()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.aliquot_type})"

    def __str__(self):
        return f"Processing profile {self.verbose_name}"

    def add_processes(self, *processes):
        """Adds processes to the processing profile or raises.
        """
        for process in processes:
            if process.aliquot_type not in self.aliquot_type.derivatives:
                raise ProcessingProfileInvalidDerivative(
                    f"Invalid process for profile. Got '{process}'. "
                    f"'{process.aliquot_type}' cannot be derived "
                    f"from '{self.aliquot_type}'."
                )
            if process.name in self.processes:
                raise ProcessingProfileAlreadyAdded(
                    f"Process '{process.name}' has already been added "
                    f"to this processing profile ('{self.name}')."
                )
            self.processes.update({process.name: process})
