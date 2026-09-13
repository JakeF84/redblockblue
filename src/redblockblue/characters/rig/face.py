"""Low-level eyebrow and mouth geometry for the character rig."""

from __future__ import annotations

import numpy as np
from manim import (
    BLACK, CubicBezier, Ellipse, Line, OUT, RIGHT, UP,
    UpdateFromAlphaFunc, VGroup, VectorizedPoint, smooth,
)

from ...core.geometry import unit_vector
from ...core.timing import positive_time

class _FaceAnchor(VGroup):
    """Minimal invisible transform frame for face-local coordinates."""

    MARKER_OFFSET = 0.01

    def __init__(self, position: np.ndarray) -> None:
        position = np.asarray(position, dtype=float)
        centre = VectorizedPoint(position)
        right = VectorizedPoint(position + self.MARKER_OFFSET * RIGHT)
        up = VectorizedPoint(position + self.MARKER_OFFSET * UP)
        super().__init__(centre, right, up)

    @property
    def centre_marker(self) -> VectorizedPoint:
        return self[0]

    @property
    def right_marker(self) -> VectorizedPoint:
        return self[1]

    @property
    def up_marker(self) -> VectorizedPoint:
        return self[2]

    def get_center(self) -> np.ndarray:
        return np.asarray(self.centre_marker.get_center(), dtype=float)

    def local_basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        centre = self.get_center()
        local_right = unit_vector(
            self.right_marker.get_center() - centre,
            fallback=RIGHT,
        )
        local_up = unit_vector(
            self.up_marker.get_center() - centre,
            fallback=UP,
        )
        normal = unit_vector(
            np.cross(local_right, local_up),
            fallback=OUT,
        )
        return local_right, local_up, normal


class CharacterEyebrowPair(VGroup):
    """Two simple brows controlled in character-local face coordinates.

    ``height`` values are offsets from the neutral brow height. ``angle``
    values are radians measured counter-clockwise in the character's face
    plane. This makes asymmetrical poses such as furrows and cocked brows easy
    to animate while remaining correct after the cube rotates in 3D.
    """

    X_POSITIONS = (-0.32, 0.32)
    Y_POSITION = 0.58
    WIDTH = 0.38
    STROKE_WIDTH = 7

    MIN_HEIGHT = -0.18
    MAX_HEIGHT = 0.22
    MAX_ABS_ANGLE = 40 * np.pi / 180

    ANCHOR_INDEX = 0
    LEFT_INDEX = 1
    RIGHT_INDEX = 2

    def __init__(
        self,
        face_depth: float,
        *,
        colour=BLACK,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.colour = colour
        self._camera_opacity = 1.0
        self._left_height = 0.0
        self._right_height = 0.0
        self._left_angle = 0.0
        self._right_angle = 0.0

        anchor = _FaceAnchor(face_depth * OUT)
        placeholder = face_depth * OUT
        left = Line(
            placeholder - 0.01 * RIGHT,
            placeholder + 0.01 * RIGHT,
            color=colour,
        )
        right = left.copy()

        self.add(anchor, left, right)
        self._apply_state()

    @property
    def anchor(self) -> _FaceAnchor:
        return self[self.ANCHOR_INDEX]

    @property
    def left(self) -> Line:
        return self[self.LEFT_INDEX]

    @property
    def right(self) -> Line:
        return self[self.RIGHT_INDEX]

    def local_basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.anchor.local_basis()

    def _brow_endpoints(
        self,
        *,
        x: float,
        height: float,
        angle: float,
        local_right: np.ndarray,
        local_up: np.ndarray,
        normal: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        centre = (
            self.anchor.get_center()
            + x * local_right
            + (self.Y_POSITION + height) * local_up
            + 0.001 * normal
        )
        direction = (
            np.cos(angle) * local_right
            + np.sin(angle) * local_up
        )
        half_span = 0.5 * self.WIDTH * direction
        return centre - half_span, centre + half_span

    @staticmethod
    def _clamp_height(value: float) -> float:
        return float(
            np.clip(
                value,
                CharacterEyebrowPair.MIN_HEIGHT,
                CharacterEyebrowPair.MAX_HEIGHT,
            )
        )

    @staticmethod
    def _clamp_angle(value: float) -> float:
        return float(
            np.clip(
                value,
                -CharacterEyebrowPair.MAX_ABS_ANGLE,
                CharacterEyebrowPair.MAX_ABS_ANGLE,
            )
        )

    def _apply_state(self) -> None:
        local_right, local_up, normal = self.local_basis()
        left_start, left_end = self._brow_endpoints(
            x=self.X_POSITIONS[0],
            height=self._left_height,
            angle=self._left_angle,
            local_right=local_right,
            local_up=local_up,
            normal=normal,
        )
        right_start, right_end = self._brow_endpoints(
            x=self.X_POSITIONS[1],
            height=self._right_height,
            angle=self._right_angle,
            local_right=local_right,
            local_up=local_up,
            normal=normal,
        )
        self.left.put_start_and_end_on(left_start, left_end)
        self.right.put_start_and_end_on(right_start, right_end)
        self.left.set_stroke(
            color=self.colour,
            width=self.STROKE_WIDTH,
            opacity=self._camera_opacity,
        )
        self.right.set_stroke(
            color=self.colour,
            width=self.STROKE_WIDTH,
            opacity=self._camera_opacity,
        )

    def set_pose(
        self,
        *,
        left_height: float = 0.0,
        right_height: float = 0.0,
        left_angle: float = 0.0,
        right_angle: float = 0.0,
    ) -> CharacterEyebrowPair:
        self._left_height = self._clamp_height(left_height)
        self._right_height = self._clamp_height(right_height)
        self._left_angle = self._clamp_angle(left_angle)
        self._right_angle = self._clamp_angle(right_angle)
        self._apply_state()
        return self

    def pose_animation(
        self,
        *,
        left_height: float = 0.0,
        right_height: float = 0.0,
        left_angle: float = 0.0,
        right_angle: float = 0.0,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        run_time = positive_time(run_time)

        start = np.array(
            [
                self._left_height,
                self._right_height,
                self._left_angle,
                self._right_angle,
            ],
            dtype=float,
        )
        end = np.array(
            [
                self._clamp_height(left_height),
                self._clamp_height(right_height),
                self._clamp_angle(left_angle),
                self._clamp_angle(right_angle),
            ],
            dtype=float,
        )

        def update_state(brows: CharacterEyebrowPair, alpha: float) -> None:
            values = (1.0 - alpha) * start + alpha * end
            (
                brows._left_height,
                brows._right_height,
                brows._left_angle,
                brows._right_angle,
            ) = (float(value) for value in values)
            brows._apply_state()

        return UpdateFromAlphaFunc(
            self,
            update_state,
            run_time=run_time,
            rate_func=rate_func,
        )

    def set_opacity(self, opacity: float) -> CharacterEyebrowPair:
        self._camera_opacity = float(np.clip(opacity, 0.0, 1.0))
        self.left.set_stroke(opacity=self._camera_opacity)
        self.right.set_stroke(opacity=self._camera_opacity)
        return self


class CharacterMouth(VGroup):
    """Minimal mouth supporting curved closed poses and an open-mouth shape.

    ``curve`` ranges from -1 (frown) through 0 (neutral) to +1 (smile).
    ``open_amount`` ranges from 0 (closed line) to 1 (fully open ellipse).
    """

    Y_POSITION = -0.38
    DEFAULT_WIDTH = 0.55
    DEFAULT_OPEN_HEIGHT = 0.30
    CURVE_DEPTH = 0.002
    OPEN_DEPTH = 0.001
    MAX_CURVE = 0.18
    STROKE_WIDTH = 6

    ANCHOR_INDEX = 0
    CURVE_INDEX = 1
    OPEN_INDEX = 2

    def __init__(
        self,
        face_depth: float,
        *,
        colour=BLACK,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.colour = colour
        self._camera_opacity = 1.0
        self._curve_amount = 0.0
        self._open_amount = 0.0
        self._width = self.DEFAULT_WIDTH
        self._open_height = self.DEFAULT_OPEN_HEIGHT

        anchor = _FaceAnchor(face_depth * OUT)
        placeholder = face_depth * OUT
        curve = CubicBezier(
            placeholder,
            placeholder,
            placeholder,
            placeholder,
        )
        open_shape = Ellipse(
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_OPEN_HEIGHT,
        ).move_to(placeholder)

        self.add(anchor, curve, open_shape)
        self._apply_state()

    @property
    def anchor(self) -> _FaceAnchor:
        return self[self.ANCHOR_INDEX]

    @property
    def curve(self) -> CubicBezier:
        return self[self.CURVE_INDEX]

    @property
    def open_shape(self) -> Ellipse:
        return self[self.OPEN_INDEX]

    def local_basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.anchor.local_basis()

    @staticmethod
    def _frame_point(
        centre: np.ndarray,
        local_right: np.ndarray,
        local_up: np.ndarray,
        normal: np.ndarray,
        x: float,
        y: float,
        depth: float,
    ) -> np.ndarray:
        return (
            centre
            + x * local_right
            + y * local_up
            + depth * normal
        )

    def _curve_geometry(
        self,
        frame: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ) -> CubicBezier:
        centre, local_right, local_up, normal = frame
        half_width = 0.5 * self._width
        centre_y = self.Y_POSITION
        bend = self.MAX_CURVE * self._curve_amount

        def point(x: float, y: float, depth: float) -> np.ndarray:
            return self._frame_point(
                centre, local_right, local_up, normal, x, y, depth
            )

        curve = CubicBezier(
            point(-half_width, centre_y, self.CURVE_DEPTH),
            point(-half_width / 3, centre_y - bend, self.CURVE_DEPTH),
            point(half_width / 3, centre_y - bend, self.CURVE_DEPTH),
            point(half_width, centre_y, self.CURVE_DEPTH),
        )
        curve.set_fill(opacity=0)
        curve.set_stroke(
            self.colour,
            width=self.STROKE_WIDTH,
            opacity=self._camera_opacity * (1.0 - self._open_amount),
        )
        return curve

    def _open_geometry(
        self,
        frame: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ) -> Ellipse:
        centre, local_right, local_up, normal = frame
        width = self._width
        height = max(0.02, self._open_height * self._open_amount)

        mouth = Ellipse(
            width=width,
            height=height,
            fill_color=self.colour,
            fill_opacity=self._camera_opacity * self._open_amount,
            stroke_color=self.colour,
            stroke_width=self.STROKE_WIDTH,
        )

        # Ellipse is created in the XY plane; map that basis onto the current
        # character face so mouth changes remain correct after 3D rotations.
        basis = np.column_stack((local_right, local_up, normal))
        mouth.apply_matrix(basis)
        mouth.move_to(
            self._frame_point(
                centre,
                local_right,
                local_up,
                normal,
                0.0,
                self.Y_POSITION,
                self.OPEN_DEPTH,
            )
        )
        mouth.set_stroke(
            opacity=self._camera_opacity * self._open_amount,
        )
        return mouth

    @staticmethod
    def _clamp_curve(value: float) -> float:
        return float(np.clip(value, -1.0, 1.0))

    @staticmethod
    def _clamp_open(value: float) -> float:
        return float(np.clip(value, 0.0, 1.0))

    def _apply_state(self) -> None:
        local_right, local_up, normal = self.local_basis()
        frame = (
            np.asarray(self.anchor.get_center(), dtype=float),
            local_right,
            local_up,
            normal,
        )
        self.curve.become(self._curve_geometry(frame))
        self.open_shape.become(self._open_geometry(frame))

    def set_pose(
        self,
        *,
        curve: float = 0.0,
        open_amount: float = 0.0,
        width: float | None = None,
        open_height: float | None = None,
    ) -> CharacterMouth:
        self._curve_amount = self._clamp_curve(curve)
        self._open_amount = self._clamp_open(open_amount)
        if width is not None:
            if width <= 0:
                raise ValueError("width must be greater than zero")
            self._width = float(width)
        if open_height is not None:
            if open_height <= 0:
                raise ValueError("open_height must be greater than zero")
            self._open_height = float(open_height)
        self._apply_state()
        return self

    def pose_animation(
        self,
        *,
        curve: float = 0.0,
        open_amount: float = 0.0,
        width: float | None = None,
        open_height: float | None = None,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        run_time = positive_time(run_time)

        start = np.array(
            [
                self._curve_amount,
                self._open_amount,
                self._width,
                self._open_height,
            ],
            dtype=float,
        )
        end_width = self._width if width is None else float(width)
        end_height = (
            self._open_height if open_height is None else float(open_height)
        )
        if end_width <= 0:
            raise ValueError("width must be greater than zero")
        if end_height <= 0:
            raise ValueError("open_height must be greater than zero")

        end = np.array(
            [
                self._clamp_curve(curve),
                self._clamp_open(open_amount),
                end_width,
                end_height,
            ],
            dtype=float,
        )

        def update_state(mouth: CharacterMouth, alpha: float) -> None:
            values = (1.0 - alpha) * start + alpha * end
            (
                mouth._curve_amount,
                mouth._open_amount,
                mouth._width,
                mouth._open_height,
            ) = (float(value) for value in values)
            mouth._apply_state()

        return UpdateFromAlphaFunc(
            self,
            update_state,
            run_time=run_time,
            rate_func=rate_func,
        )

    def set_opacity(self, opacity: float) -> CharacterMouth:
        self._camera_opacity = float(np.clip(opacity, 0.0, 1.0))
        closed_opacity = self._camera_opacity * (1.0 - self._open_amount)
        open_opacity = self._camera_opacity * self._open_amount
        self.curve.set_stroke(opacity=closed_opacity)
        self.open_shape.set_fill(opacity=open_opacity)
        self.open_shape.set_stroke(opacity=open_opacity)
        return self
__all__ = ["CharacterEyebrowPair", "CharacterMouth"]
