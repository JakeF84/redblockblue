"""Data-only facial expression vocabulary.

This module intentionally has no dependency on character controllers. Poses are
immutable data, making the vocabulary easy to tune, test, serialize, or replace.
"""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ExpressionPose:
    """Complete facial pose expressed in the rig's primitive controls."""

    category: str
    description: str
    gaze: str = "centre"
    gaze_amount: float = 0.06
    pupil_scale: float = 1.0
    upper_lid: float = 0.0
    lower_lid: float = 0.0
    left_brow_height: float = 0.0
    right_brow_height: float = 0.0
    left_brow_angle: float = 0.0
    right_brow_angle: float = 0.0
    mouth_curve: float = 0.0
    mouth_open: float = 0.0
    mouth_width: float = 0.55
    mouth_height: float = 0.30


# Angles are radians. Keeping the values here rather than scattering them
# through methods makes the entire expression vocabulary easy to tune.
DEG = 3.141592653589793 / 180.0


def _pose(category: str, description: str, **kwargs) -> ExpressionPose:
    return ExpressionPose(category=category, description=description, **kwargs)


EXPRESSION_PRESETS: dict[str, ExpressionPose] = {
    # Neutral / positive -------------------------------------------------
    "neutral": _pose("neutral", "Relaxed, attentive baseline."),
    "happy": _pose(
        "positive", "Warm happiness.", pupil_scale=1.08,
        upper_lid=0.05, lower_lid=0.18,
        left_brow_height=0.03, right_brow_height=0.03,
        mouth_curve=0.78,
    ),
    "delighted": _pose(
        "positive", "Bright, delighted pleasure.", pupil_scale=1.18,
        upper_lid=0.10, lower_lid=0.28,
        left_brow_height=0.08, right_brow_height=0.08,
        mouth_curve=0.90, mouth_open=0.22, mouth_width=0.64,
    ),
    "excited": _pose(
        "positive", "High-energy anticipation or excitement.", pupil_scale=1.35,
        left_brow_height=0.13, right_brow_height=0.13,
        mouth_curve=0.75, mouth_open=0.48, mouth_width=0.65,
    ),
    "ecstatic": _pose(
        "positive", "Maximum joy / excitement.", pupil_scale=1.48,
        upper_lid=0.10, lower_lid=0.22,
        left_brow_height=0.16, right_brow_height=0.16,
        mouth_curve=0.85, mouth_open=0.72, mouth_width=0.68, mouth_height=0.34,
    ),
    "amused": _pose(
        "positive", "Quietly amused.", gaze="right", gaze_amount=0.035,
        pupil_scale=1.03, upper_lid=0.18, lower_lid=0.24,
        left_brow_height=0.02, right_brow_height=0.07,
        mouth_curve=0.55,
    ),
    "grinning": _pose(
        "positive", "Big closed-mouth grin.", pupil_scale=1.14,
        upper_lid=0.08, lower_lid=0.30,
        left_brow_height=0.05, right_brow_height=0.05,
        mouth_curve=1.0, mouth_width=0.70,
    ),
    "laughing": _pose(
        "positive", "Open laughter with strongly narrowed eyes.", pupil_scale=1.05,
        upper_lid=0.62, lower_lid=0.42,
        left_brow_height=0.08, right_brow_height=0.08,
        mouth_curve=0.90, mouth_open=0.78, mouth_width=0.66, mouth_height=0.34,
    ),
    "holding_laughter": _pose(
        "positive", "Trying not to laugh.", gaze="left", gaze_amount=0.03,
        pupil_scale=1.0, upper_lid=0.22, lower_lid=0.52,
        left_brow_height=0.02, right_brow_height=0.02,
        mouth_curve=0.72, mouth_width=0.52,
    ),
    "relieved": _pose(
        "positive", "Tension releasing into relief.", pupil_scale=0.98,
        upper_lid=0.32, lower_lid=0.12,
        left_brow_height=0.04, right_brow_height=0.04,
        left_brow_angle=7*DEG, right_brow_angle=-7*DEG,
        mouth_curve=0.30,
    ),
    "affectionate": _pose(
        "positive", "Soft fondness / affection.", pupil_scale=1.25,
        upper_lid=0.14, lower_lid=0.24,
        left_brow_height=0.07, right_brow_height=0.07,
        mouth_curve=0.58,
    ),
    "proud": _pose(
        "positive", "Self-satisfied pride.", gaze="up", gaze_amount=0.025,
        pupil_scale=1.0, upper_lid=0.12,
        left_brow_height=0.06, right_brow_height=0.06,
        mouth_curve=0.32,
    ),
    "confident": _pose(
        "positive", "Calm confidence.", pupil_scale=1.0,
        upper_lid=0.15, lower_lid=0.05,
        left_brow_height=0.02, right_brow_height=0.02,
        mouth_curve=0.25,
    ),
    "smug": _pose(
        "positive", "Self-satisfied side-eye.", gaze="right", gaze_amount=0.05,
        pupil_scale=0.95, upper_lid=0.34, lower_lid=0.08,
        left_brow_height=0.01, right_brow_height=0.12,
        mouth_curve=0.45, mouth_width=0.48,
    ),

    # Attention / cognition ---------------------------------------------
    "curious": _pose(
        "cognitive", "Curious and inquisitive.", gaze="up_right", gaze_amount=0.05,
        pupil_scale=1.10, left_brow_height=0.03, right_brow_height=0.13,
        mouth_open=0.08, mouth_width=0.48,
    ),
    "interested": _pose(
        "cognitive", "Engaged attention.", gaze="up", gaze_amount=0.025,
        pupil_scale=1.12,
        left_brow_height=0.08, right_brow_height=0.08,
        mouth_curve=0.10,
    ),
    "thinking": _pose(
        "cognitive", "Actively thinking / considering.", gaze="up_right", gaze_amount=0.045,
        pupil_scale=0.96, upper_lid=0.14,
        left_brow_height=0.01, right_brow_height=0.10,
        mouth_curve=-0.10, mouth_width=0.48,
    ),
    "focused": _pose(
        "cognitive", "Concentrated focus.", pupil_scale=0.86,
        upper_lid=0.28, lower_lid=0.08,
        left_brow_height=-0.03, right_brow_height=-0.03,
        left_brow_angle=-8*DEG, right_brow_angle=8*DEG,
    ),
    "determined": _pose(
        "cognitive", "Firm determination.", pupil_scale=0.90,
        upper_lid=0.36, lower_lid=0.14,
        left_brow_height=-0.04, right_brow_height=-0.04,
        left_brow_angle=-13*DEG, right_brow_angle=13*DEG,
        mouth_curve=-0.18,
    ),
    "confused": _pose(
        "cognitive", "Confusion / uncertainty.", gaze="left", gaze_amount=0.035,
        pupil_scale=1.05, upper_lid=0.12,
        left_brow_height=0.13, right_brow_height=-0.02,
        left_brow_angle=-5*DEG, right_brow_angle=8*DEG,
        mouth_curve=-0.12,
    ),
    "puzzled": _pose(
        "cognitive", "Trying to make sense of something.", gaze="up_left", gaze_amount=0.04,
        pupil_scale=1.04, upper_lid=0.10,
        left_brow_height=-0.01, right_brow_height=0.14,
        left_brow_angle=-8*DEG, right_brow_angle=4*DEG,
        mouth_open=0.10, mouth_width=0.46,
    ),
    "sceptical": _pose(
        "cognitive", "Sceptical / unconvinced.", gaze="right", gaze_amount=0.05,
        pupil_scale=0.94, upper_lid=0.38, lower_lid=0.16,
        left_brow_height=-0.01, right_brow_height=0.13,
        mouth_curve=-0.06, mouth_width=0.48,
    ),
    "suspicious": _pose(
        "cognitive", "Narrow-eyed suspicion.", gaze="right", gaze_amount=0.05,
        pupil_scale=0.86, upper_lid=0.48, lower_lid=0.20,
        left_brow_height=-0.04, right_brow_height=-0.04,
        left_brow_angle=-12*DEG, right_brow_angle=12*DEG,
        mouth_curve=-0.14,
    ),
    "doubtful": _pose(
        "cognitive", "Hesitant doubt.", gaze="down_left", gaze_amount=0.035,
        pupil_scale=0.92, upper_lid=0.30, lower_lid=0.05,
        left_brow_height=0.10, right_brow_height=0.00,
        mouth_curve=-0.18,
    ),

    # Low-energy / negative ---------------------------------------------
    "unimpressed": _pose(
        "low_energy", "Unimpressed side-eye.", gaze="right", gaze_amount=0.05,
        pupil_scale=0.90, upper_lid=0.56, lower_lid=0.06,
        left_brow_height=-0.02, right_brow_height=0.02,
        mouth_curve=-0.08,
    ),
    "deadpan": _pose(
        "low_energy", "Flat, deadpan reaction.", pupil_scale=0.86,
        upper_lid=0.44, lower_lid=0.02, mouth_curve=0.0,
    ),
    "bored": _pose(
        "low_energy", "Bored / disengaged.", gaze="down", gaze_amount=0.025,
        pupil_scale=0.86, upper_lid=0.60, lower_lid=0.02,
        left_brow_height=-0.03, right_brow_height=-0.03,
        mouth_curve=-0.04,
    ),
    "fed_up": _pose(
        "low_energy", "Fed up, with an upward eye-roll feel.", gaze="up", gaze_amount=0.055,
        pupil_scale=0.88, upper_lid=0.54, lower_lid=0.03,
        left_brow_height=-0.04, right_brow_height=-0.04,
        mouth_curve=-0.24,
    ),
    "tired": _pose(
        "low_energy", "Fatigued.", gaze="down", gaze_amount=0.02,
        pupil_scale=0.92, upper_lid=0.66, lower_lid=0.02,
        left_brow_height=-0.02, right_brow_height=-0.02,
        mouth_curve=-0.04,
    ),
    "sleepy": _pose(
        "low_energy", "Very sleepy / nearly dozing.", gaze="down", gaze_amount=0.015,
        pupil_scale=0.90, upper_lid=0.78, lower_lid=0.04,
        left_brow_height=-0.03, right_brow_height=-0.03,
        mouth_open=0.14, mouth_width=0.42, mouth_height=0.22,
    ),
    "annoyed": _pose(
        "negative", "Mild irritation.", gaze="right", gaze_amount=0.04,
        pupil_scale=0.90, upper_lid=0.44, lower_lid=0.10,
        left_brow_height=-0.04, right_brow_height=-0.04,
        left_brow_angle=-9*DEG, right_brow_angle=9*DEG,
        mouth_curve=-0.24,
    ),
    "frustrated": _pose(
        "negative", "Frustration / exasperation.", gaze="down", gaze_amount=0.03,
        pupil_scale=0.88, upper_lid=0.34, lower_lid=0.10,
        left_brow_height=-0.05, right_brow_height=-0.05,
        left_brow_angle=-14*DEG, right_brow_angle=14*DEG,
        mouth_curve=-0.48,
    ),

    # Sadness / vulnerability -------------------------------------------
    "sad": _pose(
        "sadness", "Clear sadness.", gaze="down", gaze_amount=0.035,
        pupil_scale=0.96, upper_lid=0.18,
        left_brow_height=0.04, right_brow_height=0.04,
        left_brow_angle=14*DEG, right_brow_angle=-14*DEG,
        mouth_curve=-0.72,
    ),
    "disappointed": _pose(
        "sadness", "Disappointment / let-down.", gaze="down", gaze_amount=0.035,
        pupil_scale=0.90, upper_lid=0.36,
        left_brow_height=0.02, right_brow_height=0.02,
        left_brow_angle=10*DEG, right_brow_angle=-10*DEG,
        mouth_curve=-0.42,
    ),
    "worried": _pose(
        "fear", "Concerned worry.", pupil_scale=0.92, upper_lid=0.06,
        left_brow_height=0.08, right_brow_height=0.08,
        left_brow_angle=14*DEG, right_brow_angle=-14*DEG,
        mouth_curve=-0.30,
    ),
    "concerned": _pose(
        "fear", "Mild concern.", gaze="down", gaze_amount=0.025,
        pupil_scale=0.96, upper_lid=0.12,
        left_brow_height=0.06, right_brow_height=0.06,
        left_brow_angle=10*DEG, right_brow_angle=-10*DEG,
        mouth_curve=-0.20,
    ),
    "anxious": _pose(
        "fear", "Uneasy anxiety.", gaze="right", gaze_amount=0.035,
        pupil_scale=0.78,
        left_brow_height=0.11, right_brow_height=0.11,
        left_brow_angle=15*DEG, right_brow_angle=-15*DEG,
        mouth_open=0.14, mouth_width=0.46, mouth_height=0.22,
    ),
    "afraid": _pose(
        "fear", "Visible fear.", pupil_scale=0.64,
        left_brow_height=0.14, right_brow_height=0.14,
        left_brow_angle=16*DEG, right_brow_angle=-16*DEG,
        mouth_open=0.36, mouth_width=0.50, mouth_height=0.28,
    ),
    "terrified": _pose(
        "fear", "Extreme fear / panic.", pupil_scale=0.46,
        left_brow_height=0.18, right_brow_height=0.18,
        left_brow_angle=18*DEG, right_brow_angle=-18*DEG,
        mouth_open=0.82, mouth_width=0.56, mouth_height=0.38,
    ),
    "pleading": _pose(
        "vulnerable", "Pleading / puppy-eyed appeal.", gaze="up", gaze_amount=0.03,
        pupil_scale=1.34, upper_lid=0.06, lower_lid=0.12,
        left_brow_height=0.12, right_brow_height=0.12,
        left_brow_angle=15*DEG, right_brow_angle=-15*DEG,
        mouth_curve=-0.20,
    ),
    "guilty": _pose(
        "vulnerable", "Guilty / sheepish.", gaze="down_left", gaze_amount=0.035,
        pupil_scale=0.88, upper_lid=0.36,
        left_brow_height=0.06, right_brow_height=0.06,
        left_brow_angle=11*DEG, right_brow_angle=-11*DEG,
        mouth_curve=-0.16,
    ),
    "embarrassed": _pose(
        "vulnerable", "Embarrassed but warm.", gaze="down_right", gaze_amount=0.035,
        pupil_scale=1.08, upper_lid=0.20, lower_lid=0.16,
        left_brow_height=0.08, right_brow_height=0.08,
        left_brow_angle=8*DEG, right_brow_angle=-8*DEG,
        mouth_curve=0.18,
    ),
    "awkward": _pose(
        "vulnerable", "Socially awkward / unsure.", gaze="left", gaze_amount=0.045,
        pupil_scale=1.0, upper_lid=0.22,
        left_brow_height=0.10, right_brow_height=-0.01,
        mouth_curve=-0.05, mouth_width=0.46,
    ),

    # Surprise / aversion / anger ---------------------------------------
    "surprised": _pose(
        "surprise", "Ordinary surprise.", pupil_scale=0.88,
        left_brow_height=0.15, right_brow_height=0.15,
        mouth_open=0.58, mouth_width=0.52, mouth_height=0.32,
    ),
    "startled": _pose(
        "surprise", "Abrupt startle reaction.", pupil_scale=0.66,
        left_brow_height=0.17, right_brow_height=0.17,
        mouth_open=0.48, mouth_width=0.48, mouth_height=0.29,
    ),
    "shocked": _pose(
        "surprise", "Strong shock with tiny pupils.", pupil_scale=0.42,
        left_brow_height=0.19, right_brow_height=0.19,
        mouth_open=0.90, mouth_width=0.56, mouth_height=0.40,
    ),
    "disgusted": _pose(
        "aversion", "Disgust / revulsion.", gaze="down", gaze_amount=0.025,
        pupil_scale=0.82, upper_lid=0.42, lower_lid=0.24,
        left_brow_height=-0.04, right_brow_height=0.02,
        left_brow_angle=-12*DEG, right_brow_angle=7*DEG,
        mouth_curve=-0.66, mouth_width=0.48,
    ),
    "angry": _pose(
        "anger", "Clear anger.", pupil_scale=0.88,
        upper_lid=0.48, lower_lid=0.12,
        left_brow_height=-0.04, right_brow_height=-0.04,
        left_brow_angle=-16*DEG, right_brow_angle=16*DEG,
        mouth_curve=-0.46,
    ),
    "furious": _pose(
        "anger", "Extreme anger.", pupil_scale=0.72,
        upper_lid=0.60, lower_lid=0.20,
        left_brow_height=-0.06, right_brow_height=-0.06,
        left_brow_angle=-20*DEG, right_brow_angle=20*DEG,
        mouth_curve=-0.74, mouth_open=0.34, mouth_width=0.58,
    ),
    "contemptuous": _pose(
        "aversion", "Contempt / superiority.", gaze="left", gaze_amount=0.045,
        pupil_scale=0.90, upper_lid=0.46, lower_lid=0.08,
        left_brow_height=0.12, right_brow_height=-0.03,
        mouth_curve=0.30, mouth_width=0.46,
    ),
    "mischievous": _pose(
        "playful", "Mischief / plotting something playful.", gaze="right", gaze_amount=0.045,
        pupil_scale=1.05, upper_lid=0.26, lower_lid=0.16,
        left_brow_height=0.00, right_brow_height=0.12,
        mouth_curve=0.58, mouth_width=0.50,
    ),
}


__all__ = ["ExpressionPose", "EXPRESSION_PRESETS"]
