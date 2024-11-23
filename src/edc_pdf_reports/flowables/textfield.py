from reportlab.lib import colors
from reportlab.platypus import Flowable


class TextFieldFlowable(Flowable):
    def __init__(
        self,
        name: str,
        width: int | None = None,
        height: int | None = None,
        value: str = "",
        **kwargs,
    ):
        Flowable.__init__(self)
        self.name = name
        self.width = width
        self.height = height
        self.value = value
        self.extra_options = kwargs

    def draw(self):
        # Calculate the position based on the current coordinates
        x = self.canv._currentMatrix[4]
        y = self.canv._currentMatrix[5]

        options = dict(
            name=self.name,
            tooltip=self.name,
            x=x,
            y=y,
            width=self.width,
            height=self.height,
            borderStyle="underlined",
            fillColor=colors.white,
            textColor=colors.black,
            forceBorder=False,
            value=self.value,
        )
        options.update(self.extra_options)
        self.canv.acroForm.textfield(**options)

    def split(self, availWidth, availHeight):
        return [self]
