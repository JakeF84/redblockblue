import numpy as np
import pytest
from manim import ImageMobject, Scene

from redblockblue import CodeStyle, CodeWindow, Quote, QuoteStyle


@pytest.mark.parametrize("style", list(CodeStyle))
def test_code_styles_keep_component_and_clean_layers(style):
    scene = Scene(skip_animations=True)
    editor = CodeWindow("first = 1\n\nlast = 3", style=style)
    scene.play(editor.show(run_time=0.2))
    assert scene.mobjects == [editor]
    assert editor.line_count == 3
    for action in (editor.highlight, editor.error, editor.success):
        scene.play(action((2, 3)))
        assert scene.mobjects == [editor]
        assert len(editor.highlight_layer.submobjects) == 1
    scene.play(editor.clear_highlight())
    assert not editor.highlight_layer.submobjects
    for lines in (2, (1, 3), []):
        scene.play(editor.focus(lines))
        assert scene.mobjects == [editor]
        scene.play(editor.unfocus())
        assert not editor.focus_layer.submobjects
    scene.play(editor.hide())
    assert not scene.mobjects
    scene.play(editor.show(run_time=0.2))
    assert scene.mobjects == [editor]


@pytest.mark.parametrize("style", list(QuoteStyle))
@pytest.mark.parametrize("with_image", [False, True])
def test_quote_styles_show_and_hide_as_one_component(style, with_image):
    scene = Scene(skip_animations=True)
    portrait = ImageMobject(np.full((16, 16, 3), 255, dtype=np.uint8)) if with_image else None
    quote = Quote("A short quote for testing.", "An author", portrait, style=style)
    scene.play(quote.show(run_time=0.2))
    assert scene.mobjects == [quote]
    scene.play(quote.hide(run_time=0.2))
    assert not scene.mobjects


def test_empty_selections_and_inclusive_ranges():
    scene = Scene(skip_animations=True)
    editor = CodeWindow("a\n\nc")
    assert editor._normalise_lines((3, 1)) == [1, 2, 3]
    assert editor._normalise_lines([3, 1, 3]) == [3, 1]
    for action in (editor.highlight, editor.error, editor.success, editor.indicate):
        scene.play(action([]))
    with pytest.raises(TypeError):
        editor.line(True)
    with pytest.raises(ValueError):
        editor.focus(4)


@pytest.mark.parametrize("text", ["", "\n", "   "])
@pytest.mark.parametrize("component", [Quote, CodeWindow])
def test_empty_content_has_a_clear_error(component, text):
    with pytest.raises(ValueError, match="non-whitespace"):
        component(text)


@pytest.mark.parametrize("component", [
    lambda: CodeWindow("a = 1", style=CodeStyle.WALKTHROUGH),
    lambda: Quote("A staged quote", style=QuoteStyle.CARD),
])
def test_later_text_is_hidden_at_start_of_staged_entrance(component):
    scene = Scene(skip_animations=True)
    mob = component()
    entrance = mob.show()
    scene.add_mobjects_from_animations([entrance])
    entrance._setup_scene(scene)
    entrance.begin()
    text = mob.line(1) if isinstance(mob, CodeWindow) else mob.quote_lines
    glyphs = [part for part in text.get_family() if part.has_points()]
    assert glyphs
    assert all(part.get_fill_opacity() == 0 for part in glyphs)
    entrance.finish()
    entrance.clean_up_from_scene(scene)
    assert scene.mobjects == [mob]


def test_encoded_video_preserves_frames_across_clip_boundaries():
    import av
    from manim import tempconfig
    from redblockblue import RBBScene

    class RenderCheck(RBBScene):
        def construct(self):
            editor = CodeWindow(
                "def square(x):\n    return x * x", title="square.py",
                style=CodeStyle.WALKTHROUGH,
            )
            self.play(editor.show())
            self.play(editor.focus(2))
            self.play(editor.success(2))
            self.play(editor.hide())
            self.play(Quote("Programs must be written for people to read.", "Harold Abelson", style=QuoteStyle.EDITORIAL).show())

    def frames(path):
        with av.open(str(path)) as video:
            return [frame.to_ndarray(format="rgb24") for frame in video.decode(video=0)]

    with tempconfig({
        "dry_run": False, "write_to_movie": True,
        "pixel_width": 854, "pixel_height": 480, "frame_rate": 15,
    }):
        scene = RenderCheck()
        scene.render()
        writer = scene.renderer.file_writer
        combined = frames(writer.movie_file_path)
        clips = [frame for path in writer.partial_movie_files for frame in frames(path)]
    assert len(combined) == len(clips)
    for actual, expected in zip(combined, clips):
        # Combining the existing encoded packets must not change their pixels.
        np.testing.assert_array_equal(actual, expected)
