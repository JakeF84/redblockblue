import importlib
import pkgutil

import numpy as np
import pytest
from manim import PI, RIGHT, Succession, UP

from redblockblue import RBBScene
from redblockblue.characters import EXPRESSION_PRESETS
from redblockblue.core.motion import move_and_spin, move_to_point
from redblockblue.core.targets import resolve_target_point
from redblockblue.core.timing import positive_time


def test_all_public_exports_resolve():
    for package_name in ("redblockblue", "cube_characters"):
        package = importlib.import_module(package_name)
        for info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            module = importlib.import_module(info.name)
            for name in getattr(module, "__all__", ()):
                assert hasattr(module, name), (info.name, name)


@pytest.mark.parametrize("features", [True, False])
def test_armless_character_can_play_every_expression(features):
    scene = RBBScene(skip_animations=True)
    actor = scene.red(with_eyebrows=features, with_mouth=features)
    assert len(actor.mob.submobjects) == 4
    assert actor.mob.body is actor.mob.submobjects[0]
    assert not hasattr(actor, "arms")
    for name in EXPRESSION_PRESETS:
        scene.play(actor.react_animation(name, duration=0.1))
    assert np.isfinite(actor.mob.get_all_points()).all()


def test_face_hides_when_character_turns_away():
    scene = RBBScene(skip_animations=True)
    actor = scene.red(y_rotation=0, x_rotation=0)
    actor.mob.rotate(PI, axis=UP)
    actor.visibility_controller.refresh()
    assert actor.mob.eyes[0].outer.get_fill_opacity() == 0
    actor.mob.rotate(PI, axis=UP)
    actor.visibility_controller.refresh()
    assert actor.mob.eyes[0].outer.get_fill_opacity() == 1


@pytest.mark.parametrize("move", [move_to_point, move_and_spin])
def test_prebuilt_moves_resolve_start_at_playback(move):
    scene = RBBScene(skip_animations=True)
    actor = scene.red()
    first = move(actor.mob, RIGHT, run_time=0.1)
    second = move(actor.mob, 3 * RIGHT, run_time=0.1)
    scene.play(Succession(first, second))
    np.testing.assert_allclose(actor.mob.get_center(), 3 * RIGHT, atol=1e-6)


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
def test_invalid_timing_is_rejected(value):
    with pytest.raises(ValueError):
        positive_time(value)


def test_targets_accept_actors_and_points_but_reject_bad_coordinates():
    scene = RBBScene(skip_animations=True)
    actor = scene.red()
    np.testing.assert_allclose(resolve_target_point(actor), actor.mob.get_center())
    np.testing.assert_allclose(resolve_target_point([1, 2]), [1, 2, 0])
    for target in ([1], [1, 2, 3, 4], [1, float("nan")]):
        with pytest.raises(ValueError):
            resolve_target_point(target)
