from reportlab.lib import colors
from reportlab.platypus import Flowable


class CheckboxFlowable(Flowable):
    def __init__(self, name, size=10, checked=False):
        Flowable.__init__(self)
        self.name = name
        self.size = size
        self.checked = checked

    def draw(self):
        x = self.canv._currentMatrix[4] + self.size / 2 - 10
        y = self.canv._currentMatrix[5] - self.size / 2
        self.canv.acroForm.checkbox(
            name=self.name,
            tooltip=self.name,
            size=self.size,
            x=x,
            y=y,
            buttonStyle="check",
            borderStyle="solid",
            borderWidth=0.5,
            borderColor=colors.black,
            fillColor=colors.white,
            textColor=colors.black,
            forceBorder=True,
            checked=self.checked,
        )
