class ProcessingProfileError(Exception):
    pass


class Process:

    def __init__(self, aliquot_type=None, aliquot_count=None):
        self.aliquot_type = aliquot_type
        self.aliquot_count = aliquot_count
        self.name = '{}-{}'.format(str(self.aliquot_type),
                                   self.aliquot_count)

    def __repr__(self):
        return '<Process({}, {})>'.format(
            str(self.aliquot_type), self.aliquot_count)

    def __str__(self):
        return self.name


class ProcessingProfile:

    def __init__(self, name, alpha_code, verbose_name=None):
        self.aliquot_type = alpha_code
        self.name = name
        self.verbose_name = verbose_name or ' '.join(name.split('_')).title()
        self.processes = {}

    def __repr__(self):
        return '<ProcessingProfile({}, {})>'.format(
            self.name, str(self.aliquot_type))

    def __str__(self):
        return self.name

    def add_process(self, aliquot_type=None, aliquot_count=None):
        process = Process(
            aliquot_type=aliquot_type,
            aliquot_count=aliquot_count)
        if process.aliquot_type.numeric_code not in [a.numeric_code for a in self.aliquot_type.derivatives]:
            raise ProcessingProfileError(
                'Invalid process. Got \'{}\'. \'{}\' cannot be derived from \'{}\'.'.format(
                    process.name, str(process.aliquot_type), str(self.aliquot_type)))
        if process.name in self.processes:
            raise ProcessingProfileError(
                'Process {} has already been added to this procesing profile.'.format(process.name))
        self.processes.update({process.name: process})
