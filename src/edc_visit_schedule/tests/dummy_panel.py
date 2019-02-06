class DummyPanel:

    """A dummy lab panel object.
    """

    def __init__(self, name=None, verbose_name=None, requisition_model=None):
        self.name = name
        self.verbose_name = verbose_name or name
        self.requisition_model = requisition_model

    def __str__(self):
        return self.verbose_name

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
