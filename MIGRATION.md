# Migration

## Arms removed

Remove `with_arms` and `arm_kwargs` from character construction. `CharacterArm`,
`CharacterArms`, `ArmName`, `ArmSide`, `CharacterGestures`, arm constants, and the
`cube_characters.arms` module are removed. The actor no longer exposes `arms`,
`left_arm`, `right_arm`, `arm()`, `move_hand()`, `arms_neutral()`, `point_at()`,
`hand_to_chin()`, or `wave()` (including animation variants).

Replace those beats with gaze or facial expressions:

```python
red = self.red()
red.react("thinking")
red.look_at(blue)
red.react("happy")
```

Use `mob.body`, `mob.eyes`, `mob.eyebrows`, and `mob.mouth` to access geometry.
The empty arm slot is gone, so raw numeric submobject indices have changed.
The arm demo was removed; the remaining examples use face and motion controls.

## Existing imports and face controls

`from cube_characters import *` still supports the remaining character API.
For new scripts, import Manim and RedBlockBlue explicitly:

```python
from manim import LEFT, RIGHT
from redblockblue import RBBScene, CodeWindow, Quote
```

Old face shortcuts still work. Prefer `red.eyebrows.raise_()` to
`red.raise_eyebrows()`, and `red.mouth.smile()` to `red.smile()`.
`red.expressions.thinking()` and `red.react("thinking")` are equivalent.

## Presentation and movement

The code and quote constructors, styles, and action names remain available.
Entrance animations keep each component together in the scene; highlights and
focus copies are removed from their layers when cleared. Quote decorations are
vector groups so styles that draw their decorations can render correctly.

Prepare code selection actions immediately before playback. For simultaneous
character actions, use different features or different characters: a whole-face
expression and a gaze animation both move the pupils.

Prepared movement animations now capture their starting pose when played.
Bounce pauses during explicit movement and resumes afterwards. Invalid timing
(NaN, infinity, zero, or negative values) and coordinates outside finite 2D/3D
points now raise errors instead of propagating invalid geometry.
