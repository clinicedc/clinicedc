
class JobResult:
    def __init__(self, name=None, job_ids=None, copies=None, printer=None):
        self.name = name
        self.job_ids = job_ids
        if self.job_ids:
            self.print_count = len(self.job_ids)
        else:
            self.print_count = 0
        self.copies = copies
        self.printer = printer
        self.jobid = ','.join([str(i) for i in self.job_ids or [0]])

    @property
    def message(self):
        return (f'Sent {self.print_count}/{self.copies} {self.name} labels '
                f'to printer \'{self.printer.printer_info}\'. {self.job_ids}')
