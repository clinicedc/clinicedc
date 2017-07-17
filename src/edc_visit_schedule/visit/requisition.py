from .crf import Crf


class Panel:

    def __init__(self, name=None, panel_type=None,
                 aliquot_type_alpha_code=None):
        self.name = name
        self.type = panel_type
        self.aliquot_type_code = aliquot_type_alpha_code

    def __str(self):
        return self.name


class Requisition(Crf):

    def __init__(self, panel=None, **kwargs):
        super().__init__(**kwargs)
        self.panel = panel

    def __repr__(self):
        return f'{self.__class__.__name__}({self.show_order}, {self.panel})'

    def __str__(self):
        required = 'Required' if self.required else ''
        return f'{self.panel.name} {required}'
