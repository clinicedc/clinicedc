from django.contrib import messages


class JobResult:
    def __init__(self, name=None, job_ids=None, copies=None, printer=None):
        self.name = name or ""
        self.job_ids = job_ids
        if self.job_ids:
            self.print_count = len(self.job_ids)
        else:
            self.print_count = 0
        self.copies = copies
        try:
            self.printer_info = printer.printer_info
        except AttributeError:
            self.printer_info = None
        self.jobid = ",".join([str(i) for i in self.job_ids or [0]])

    @property
    def message(self):
        return (
            f"Sent {self.print_count}/{self.copies} {self.name} labels "
            f"to printer '{self.printer_info}'. {self.job_ids}"
        )


def add_job_results_to_messages(request=None, job_results=None):
    job_results = [job for job in job_results if job]
    if job_results:
        messages.success(
            request,
            JobResult(
                name=job_results[0].name,
                job_ids=sum([j.job_ids for j in job_results], []),
                copies=sum([j.print_count for j in job_results]),
                printer=job_results[0].printer_info,
            ).message,
        )
