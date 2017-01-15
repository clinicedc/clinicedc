    def appointment_wrapper(self, obj, **options):
        """Add next_url and if has a visit instance, wraps that too."""
        options.update({k: v for k, v in self.kwargs.items() if k not in options})
        obj.next_url = self.get_next_url('appointment', **options)
        obj = self.visit_wrapper(obj, **options)
        return obj
