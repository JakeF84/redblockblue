from cube_characters import *


class FaceCapabilitiesDemo(CharacterScene):
    ANIMATION_TIME = 0.45

    def construct(self):
        self.set_camera_orientation(focal_distance=1000)

        red = self.red(
            at=2.2 * LEFT,
            y_rotation=-20 * DEGREES,
            x_rotation=5 * DEGREES,
        )

        blue = self.blue(
            at=2.2 * RIGHT,
            y_rotation=20 * DEGREES,
            x_rotation=5 * DEGREES,
        )

        self.wait(0.5)

        # Eyebrow primitives.
        red.raise_eyebrows(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.furrow_eyebrows(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.worried_eyebrows(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.cock_eyebrow("right", duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.neutral_eyebrows(duration=self.ANIMATION_TIME)

        # Mouth primitives.
        red.smile(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.frown(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.open_mouth(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.surprised_mouth(duration=self.ANIMATION_TIME)
        self.wait(0.4)
        red.neutral_mouth(duration=self.ANIMATION_TIME)

        # Whole-face presets compose eyes + brows + mouth.
        red.happy(duration=self.ANIMATION_TIME)
        self.wait(0.6)
        red.sad(duration=self.ANIMATION_TIME)
        self.wait(0.6)
        red.angry(duration=self.ANIMATION_TIME)
        self.wait(0.6)
        red.surprised(duration=self.ANIMATION_TIME)
        self.wait(0.6)
        red.neutral_expression(duration=self.ANIMATION_TIME)

        # Expressions can still be composed manually and simultaneously.
        self.together(
            red.move_pupils_animation(RIGHT, duration=self.ANIMATION_TIME),
            red.cock_eyebrow_animation(
                "right",
                duration=self.ANIMATION_TIME,
            ),
            red.mouth.move_animation(
                curve=0.15,
                duration=self.ANIMATION_TIME,
            ),
        )
        self.wait(0.5)

        # Combine gaze, brows, and mouth into a thoughtful pose.
        self.together(
            red.move_pupils_animation(UP + RIGHT, duration=self.ANIMATION_TIME),
            red.cock_eyebrow_animation(
                "right",
                duration=self.ANIMATION_TIME,
            ),
            red.neutral_mouth_animation(duration=self.ANIMATION_TIME),
        )
        self.wait(1)

        red.look_at(blue)
