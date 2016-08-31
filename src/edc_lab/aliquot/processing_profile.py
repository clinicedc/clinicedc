
class Process:

    def __init__(self, alpha_code, aliquot_count):
        self.aliquot_type = alpha_code
        self.aliquot_count = aliquot_count


class ProcessingProfile:

    def __init__(self, name, alpha_code, processes=None):
        self.processes = []
        self.name = name
        self.aliquot_type = alpha_code
        for process in processes:
            self.add_process(process)

    def add_process(self, process):
        self.processes.append(process)
