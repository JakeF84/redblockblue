"""Low-level eye geometry. Scene authors should normally use actor.eyes."""

from __future__ import annotations

import numpy as np
from manim import (
    BLACK, WHITE, Circle, CubicBezier, Line, ManimColor, Mobject,
    OUT, RIGHT, UP, UpdateFromAlphaFunc, VGroup, VMobject, interpolate, smooth,
)

from ...core.geometry import unit_vector
from ...core.timing import positive_time

class CharacterEye(VGroup):
    """One eye with independently controlled upper and lower eyelids."""

    OUTER_RADIUS = 0.2
    PUPIL_RADIUS = 0.1
    PUPIL_DEPTH = 0.003

    LID_ARCH = 0.035
    LID_ARC_SAMPLES = 32
    LID_FILL_DEPTH = 0.006
    LID_EDGE_DEPTH = 0.007
    LID_EDGE_STROKE_WIDTH = 3

    CLOSED_LINE_DEPTH = 0.008
    CLOSED_LID_WIDTH = 0.27
    CLOSED_LID_STROKE_WIDTH = 5

    def __init__(
        self,
        pupil_colour: ManimColor,
        lid_colour: ManimColor,
        position: np.ndarray,
        *,
        eyes_open: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.pupil_colour = pupil_colour
        self.lid_colour = lid_colour
        self._camera_opacity = 1.0
        self._pupil_scale = 1.0

        initial_lid_amount = 0.0 if eyes_open else 1.0
        self._upper_lid_amount = initial_lid_amount
        self._lower_lid_amount = initial_lid_amount

        outer = Circle(
            radius=self.OUTER_RADIUS,
            fill_color=WHITE,
            fill_opacity=1,
            stroke_width=0,
            shade_in_3d=False,
        ).move_to(position)

        pupil = Circle(
            radius=self.PUPIL_RADIUS,
            fill_color=pupil_colour,
            fill_opacity=1,
            stroke_width=0,
            shade_in_3d=False,
        ).move_to(position + self.PUPIL_DEPTH * OUT)

        upper_lid_fill = VMobject()
        lower_lid_fill = VMobject()

        upper_lid_edge = CubicBezier(
            position,
            position,
            position,
            position,
        )
        lower_lid_edge = CubicBezier(
            position,
            position,
            position,
            position,
        )

        closed_centre = position + self.CLOSED_LINE_DEPTH * OUT
        closed_lid = Line(
            start=closed_centre - 0.5 * self.CLOSED_LID_WIDTH * RIGHT,
            end=closed_centre + 0.5 * self.CLOSED_LID_WIDTH * RIGHT,
            color=BLACK,
            stroke_width=self.CLOSED_LID_STROKE_WIDTH,
        )

        # Lids are drawn after the pupil so they cover it correctly.
        self.add(
            outer,
            pupil,
            upper_lid_fill,
            lower_lid_fill,
            upper_lid_edge,
            lower_lid_edge,
            closed_lid,
        )
        self._apply_eye_state()

    @property
    def outer(self) -> Circle:
        return self[0]

    @property
    def pupil(self) -> Circle:
        return self[1]

    @property
    def upper_lid_fill(self) -> VMobject:
        return self[2]

    @property
    def lower_lid_fill(self) -> VMobject:
        return self[3]

    @property
    def upper_lid(self) -> CubicBezier:
        return self[4]

    @property
    def lower_lid(self) -> CubicBezier:
        return self[5]

    @property
    def lid(self) -> Line:
        """Return the fully closed eye crease."""
        return self[6]

    @property
    def pupil_scale(self) -> float:
        """Pupil size multiplier relative to the neutral pupil radius."""
        return float(self._pupil_scale)

    @staticmethod
    def _clamp_pupil_scale(value: float) -> float:
        """Keep expressive pupil sizes positive and visually usable."""
        return float(np.clip(value, 0.35, 1.80))

    def set_pupil_scale(self, scale: float) -> CharacterEye:
        """Set pupil size without changing its gaze position."""
        target = self._clamp_pupil_scale(scale)
        factor = target / self._pupil_scale
        if abs(factor - 1.0) > 1e-12:
            self.pupil.scale(factor, about_point=self.pupil.get_center())
        self._pupil_scale = target
        return self

    def pupil_scale_animation(
        self,
        scale: float,
        run_time: float = 0.3,
        *,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        """Animate pupil size while preserving the current pupil centre."""
        run_time = positive_time(run_time)
        start = float(self._pupil_scale)
        end = self._clamp_pupil_scale(scale)

        def update_scale(_pupil: Mobject, alpha: float) -> None:
            target = float(interpolate(start, end, alpha))
            self.set_pupil_scale(target)

        return UpdateFromAlphaFunc(
            self.pupil,
            update_scale,
            run_time=run_time,
            rate_func=rate_func,
        )

    @property
    def upper_lid_amount(self) -> float:
        """Upper-lid closure: 0 is raised, 1 reaches the eye centre."""
        return float(self._upper_lid_amount)

    @property
    def lower_lid_amount(self) -> float:
        """Lower-lid closure: 0 is lowered, 1 reaches the eye centre."""
        return float(self._lower_lid_amount)

    @property
    def _open_amount(self) -> float:
        """Compatibility value used by older scenes.

        1 means fully open and 0 means both lids are fully closed.
        """
        return 1.0 - 0.5 * (
            self._upper_lid_amount + self._lower_lid_amount
        )

    @_open_amount.setter
    def _open_amount(self, value: float) -> None:
        closure = 1.0 - float(np.clip(value, 0.0, 1.0))
        self._upper_lid_amount = closure
        self._lower_lid_amount = closure

    @property
    def eyes_open(self) -> bool:
        return self._open_amount >= 0.5

    def _lid_frame(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return the eye centre and local basis once for one geometry update."""
        centre = np.asarray(self.outer.get_center(), dtype=float)
        local_right, local_up, normal = self.local_basis()
        return centre, local_right, local_up, normal

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

    def _upper_lid_geometry(
        self,
        amount: float,
        frame: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = None,
    ) -> tuple[VMobject, CubicBezier]:
        radius = float(self.OUTER_RADIUS)
        amount = float(np.clip(amount, 0.0, 1.0))
        if frame is None:
            frame = self._lid_frame()
        centre, local_right, local_up, normal = frame

        def point(x: float, y: float, depth: float) -> np.ndarray:
            return self._frame_point(
                centre, local_right, local_up, normal, x, y, depth
            )

        edge_y = float(
            np.clip(
                radius * (1.0 - amount),
                -radius + 1e-4,
                radius - 1e-4,
            )
        )
        half_width = float(
            np.sqrt(max(radius * radius - edge_y * edge_y, 0.0))
        )
        arch = self.LID_ARCH * 4.0 * amount * (1.0 - amount)

        left_fill = point(-half_width, edge_y, self.LID_FILL_DEPTH)
        right_fill = point(half_width, edge_y, self.LID_FILL_DEPTH)
        control_1_fill = point(
            -half_width / 3, edge_y + arch, self.LID_FILL_DEPTH
        )
        control_2_fill = point(
            half_width / 3, edge_y + arch, self.LID_FILL_DEPTH
        )

        start_angle = float(np.arcsin(edge_y / radius))
        end_angle = float(np.pi - start_angle)
        arc_angles = np.linspace(start_angle, end_angle, self.LID_ARC_SAMPLES)

        fill = VMobject()
        fill.start_new_path(left_fill)
        fill.add_cubic_bezier_curve_to(
            control_1_fill,
            control_2_fill,
            right_fill,
        )
        for angle in arc_angles[1:]:
            fill.add_line_to(
                point(
                    radius * np.cos(angle),
                    radius * np.sin(angle),
                    self.LID_FILL_DEPTH,
                )
            )
        fill.close_path()
        fill.set_fill(self.lid_colour, opacity=1)
        fill.set_stroke(width=0)
        fill.set_shade_in_3d(True)

        edge = CubicBezier(
            point(-half_width, edge_y, self.LID_EDGE_DEPTH),
            point(-half_width / 3, edge_y + arch, self.LID_EDGE_DEPTH),
            point(half_width / 3, edge_y + arch, self.LID_EDGE_DEPTH),
            point(half_width, edge_y, self.LID_EDGE_DEPTH),
        )
        edge.set_fill(opacity=0)
        edge.set_stroke(BLACK, width=self.LID_EDGE_STROKE_WIDTH)
        return fill, edge

    def _lower_lid_geometry(
        self,
        amount: float,
        frame: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = None,
    ) -> tuple[VMobject, CubicBezier]:
        radius = float(self.OUTER_RADIUS)
        amount = float(np.clip(amount, 0.0, 1.0))
        if frame is None:
            frame = self._lid_frame()
        centre, local_right, local_up, normal = frame

        def point(x: float, y: float, depth: float) -> np.ndarray:
            return self._frame_point(
                centre, local_right, local_up, normal, x, y, depth
            )

        edge_y = float(
            np.clip(
                -radius * (1.0 - amount),
                -radius + 1e-4,
                radius - 1e-4,
            )
        )
        half_width = float(
            np.sqrt(max(radius * radius - edge_y * edge_y, 0.0))
        )
        arch = self.LID_ARCH * 4.0 * amount * (1.0 - amount)

        left_fill = point(-half_width, edge_y, self.LID_FILL_DEPTH)
        right_fill = point(half_width, edge_y, self.LID_FILL_DEPTH)
        control_1_fill = point(
            -half_width / 3, edge_y - arch, self.LID_FILL_DEPTH
        )
        control_2_fill = point(
            half_width / 3, edge_y - arch, self.LID_FILL_DEPTH
        )

        start_angle = float(np.arcsin(edge_y / radius))
        end_angle = float(-np.pi - start_angle)
        arc_angles = np.linspace(start_angle, end_angle, self.LID_ARC_SAMPLES)

        fill = VMobject()
        fill.start_new_path(left_fill)
        fill.add_cubic_bezier_curve_to(
            control_1_fill,
            control_2_fill,
            right_fill,
        )
        for angle in arc_angles[1:]:
            fill.add_line_to(
                point(
                    radius * np.cos(angle),
                    radius * np.sin(angle),
                    self.LID_FILL_DEPTH,
                )
            )
        fill.close_path()
        fill.set_fill(self.lid_colour, opacity=1)
        fill.set_stroke(width=0)
        fill.set_shade_in_3d(True)

        edge = CubicBezier(
            point(-half_width, edge_y, self.LID_EDGE_DEPTH),
            point(-half_width / 3, edge_y - arch, self.LID_EDGE_DEPTH),
            point(half_width / 3, edge_y - arch, self.LID_EDGE_DEPTH),
            point(half_width, edge_y, self.LID_EDGE_DEPTH),
        )
        edge.set_fill(opacity=0)
        edge.set_stroke(BLACK, width=self.LID_EDGE_STROKE_WIDTH)
        return fill, edge

    def _update_lid_geometry(self) -> None:
        frame = self._lid_frame()
        centre, local_right, local_up, normal = frame
        upper_fill, upper_edge = self._upper_lid_geometry(
            self._upper_lid_amount, frame
        )
        lower_fill, lower_edge = self._lower_lid_geometry(
            self._lower_lid_amount, frame
        )

        self.upper_lid_fill.become(upper_fill)
        self.lower_lid_fill.become(lower_fill)
        self.upper_lid.become(upper_edge)
        self.lower_lid.become(lower_edge)

        closed_centre = self._frame_point(
            centre,
            local_right,
            local_up,
            normal,
            0.0,
            0.0,
            self.CLOSED_LINE_DEPTH,
        )
        self.lid.put_start_and_end_on(
            closed_centre - 0.5 * self.CLOSED_LID_WIDTH * local_right,
            closed_centre + 0.5 * self.CLOSED_LID_WIDTH * local_right,
        )

    def _apply_visibility_styles(self) -> None:
        """Update eye opacities without rebuilding lid geometry."""
        camera_opacity = self._camera_opacity
        upper = float(np.clip(self._upper_lid_amount, 0.0, 1.0))
        lower = float(np.clip(self._lower_lid_amount, 0.0, 1.0))

        # The visible opening is full at (0, 0) and zero at (1, 1).
        aperture = float(np.clip(1.0 - 0.5 * (upper + lower), 0.0, 1.0))
        content_visibility = float(np.clip(aperture / 0.08, 0.0, 1.0))
        upper_visibility = float(np.clip(upper / 0.08, 0.0, 1.0))
        lower_visibility = float(np.clip(lower / 0.08, 0.0, 1.0))

        # Near full closure, remove the coloured caps and eye circle so only
        # the black closed-eye crease remains.
        closed_visibility = float(
            np.clip((upper + lower - 1.8) / 0.2, 0.0, 1.0)
        )
        lid_content_visibility = 1.0 - closed_visibility

        self.outer.set_fill(opacity=camera_opacity * content_visibility)
        self.pupil.set_fill(opacity=camera_opacity * content_visibility)
        self.upper_lid_fill.set_fill(
            self.lid_colour,
            opacity=camera_opacity * upper_visibility * lid_content_visibility,
        )
        self.lower_lid_fill.set_fill(
            self.lid_colour,
            opacity=camera_opacity * lower_visibility * lid_content_visibility,
        )
        self.upper_lid_fill.set_stroke(width=0)
        self.lower_lid_fill.set_stroke(width=0)
        self.upper_lid.set_stroke(
            opacity=camera_opacity * upper_visibility * content_visibility
        )
        self.lower_lid.set_stroke(
            opacity=camera_opacity * lower_visibility * content_visibility
        )
        self.lid.set_stroke(opacity=camera_opacity * closed_visibility)

    def _apply_eye_state(self) -> None:
        self._update_lid_geometry()
        self._apply_visibility_styles()

    def set_lids(
        self,
        upper: float = 0.0,
        lower: float = 0.0,
    ) -> CharacterEye:
        self._upper_lid_amount = float(np.clip(upper, 0.0, 1.0))
        self._lower_lid_amount = float(np.clip(lower, 0.0, 1.0))
        self._apply_eye_state()
        return self

    def lids_animation(
        self,
        upper: float = 0.0,
        lower: float = 0.0,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        run_time = positive_time(run_time)

        start_upper = float(self._upper_lid_amount)
        start_lower = float(self._lower_lid_amount)
        end_upper = float(np.clip(upper, 0.0, 1.0))
        end_lower = float(np.clip(lower, 0.0, 1.0))

        def update_state(eye: CharacterEye, alpha: float) -> None:
            eye._upper_lid_amount = interpolate(
                start_upper,
                end_upper,
                alpha,
            )
            eye._lower_lid_amount = interpolate(
                start_lower,
                end_lower,
                alpha,
            )
            eye._apply_eye_state()

        return UpdateFromAlphaFunc(
            self,
            update_state,
            run_time=run_time,
            rate_func=rate_func,
        )

    def set_eyes_open(self, eyes_open: bool) -> CharacterEye:
        target = 0.0 if eyes_open else 1.0
        return self.set_lids(upper=target, lower=target)

    def state_animation(
        self,
        eyes_open: bool,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        target = 0.0 if eyes_open else 1.0
        return self.lids_animation(
            upper=target,
            lower=target,
            run_time=run_time,
            rate_func=rate_func,
        )

    def open_animation(
        self,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.state_animation(True, run_time, rate_func)

    def close_animation(
        self,
        run_time: float = 0.3,
        rate_func=smooth,
    ) -> UpdateFromAlphaFunc:
        return self.state_animation(False, run_time, rate_func)

    def local_basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        centre = self.outer.get_center()
        local_right = unit_vector(
            self.outer.point_from_proportion(0) - centre,
            fallback=RIGHT,
        )
        local_up = unit_vector(
            self.outer.point_from_proportion(0.25) - centre,
            fallback=UP,
        )
        normal = unit_vector(
            np.cross(local_right, local_up),
            fallback=OUT,
        )
        return local_right, local_up, normal

    def surface_normal(self) -> np.ndarray:
        return self.local_basis()[2]

    def pupil_target(self, x: float = 0, y: float = 0) -> np.ndarray:
        centre = self.outer.get_center()
        local_right, local_up, normal = self.local_basis()
        pupil_depth = np.dot(
            self.pupil.get_center() - centre,
            normal,
        )
        return (
            centre
            + x * local_right
            + y * local_up
            + pupil_depth * normal
        )

    def set_opacity(self, opacity: float) -> CharacterEye:
        self._camera_opacity = float(np.clip(opacity, 0.0, 1.0))
        self._apply_visibility_styles()
        return self
__all__ = ["CharacterEye"]
