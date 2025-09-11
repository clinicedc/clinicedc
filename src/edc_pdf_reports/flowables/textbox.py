from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable


class TextboxFlowable(Flowable):
    def __init__(self, name, width=200, height=60, value="", borderStyle="solid"):
        Flowable.__init__(self)
        self.name = name
        self.width = width
        self.height = height
        self.value = value
        self.borderStyle = borderStyle

    def draw(self):
        # Calculate the position based on the current coordinates
        x = self.canv._currentMatrix[4]
        y = self.canv._currentMatrix[5] - self.height

        # Draw the bottom border if borderStyle is 'underlined'
        if self.borderStyle == "underlined":
            self.canv.setStrokeColor(colors.black)
            self.canv.setLineWidth(1)
            self.canv.line(x, y, x + self.width, y)

        # Create the text area with the specified border style
        width, height = A4
        self.canv.acroForm.textfield(
            name=self.name,
            tooltip=self.name,
            x=x,
            y=y,
            width=width * 0.6,
            height=height * 0.4,
            borderStyle=(self.borderStyle if self.borderStyle != "underlined" else "none"),
            fillColor=colors.white,
            textColor=colors.black,
            forceBorder=True,
            value=self.value,
            fieldFlags="multiline",  # Enable multiline for the textbox
        )

    def split(self, availWidth, availHeight):
        return [self]
