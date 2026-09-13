from manim import *
from redblockblue import CodeStyle, CodeWindow, Quote, QuoteStyle, RBBScene


class PresentationDemo(RBBScene):
    def construct(self):
        editor = CodeWindow(
            "def square(x):\n    return x * x",
            language="python",
            title="square.py",
            style=CodeStyle.WALKTHROUGH,
        )
        self.play(editor.show())
        self.play(editor.focus(2))
        self.play(editor.success(2))
        self.play(editor.hide())

        quote = Quote(
            "Programs must be written for people to read.",
            "Harold Abelson",
            style=QuoteStyle.EDITORIAL,
        )
        self.play(quote.show())
