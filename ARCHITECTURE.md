# Architecture

Scene scripts describe actions. Controllers turn those actions into animations;
rigs own geometry. The existing separation works well and does not need another
framework layer.

- `CharacterActor` is the script-facing facade. It owns eyes, eyebrows, mouth,
  expression, and motion controllers. Add primitive operations to the relevant
  controller; promote an actor shortcut only if it improves scene readability.
- Rigs know about Manim and geometry, not quotes, code windows, or scene stories.
- `core` holds shared target resolution, timing validation, and rigid motion.
  Actor-like targets participate by exposing a `mob` property.
- Expression poses and presentation styles are data. Keep variations in their
  registries rather than duplicating methods.
- Presentation components are Manim groups. Animation groups must retain the
  component root, and transient children must be detached from their owning
  layer before scene removal. Otherwise Manim can split the parent group apart.
- Staged entrances initialize all parts at the start using lagged animation
  groups. This prevents later parts appearing before their entrance begins.
- Whole-face expressions own gaze as well as lids, brows, and mouth. Do not
  schedule another pupil animation on the same actor at the same time.
- Compatibility forwarding belongs in `_legacy.py` and `cube_characters`.
  New features belong in `redblockblue`.

Keep direct Manim access available through `actor.mob` or the presentation
component itself. Add future domains as independent components only when a
video needs them.
