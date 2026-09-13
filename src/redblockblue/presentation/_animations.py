"""Scene-graph cleanup shared by presentation animations."""

from manim import FadeOut, Mobject, Scene


class RemoveFromLayer(FadeOut):
    """Fade out a child without Manim dissolving its component's scene root."""

    def __init__(self, mobject: Mobject, layer: Mobject, **kwargs):
        self.layer = layer
        super().__init__(mobject, **kwargs)

    def clean_up_from_scene(self, scene: Scene) -> None:
        self.layer.remove(self.mobject)
        super().clean_up_from_scene(scene)
