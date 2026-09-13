"""Compatibility package for the original ``cube_characters`` API."""

from manim import *
from .actor import *
from .constants import *
from .eyes import *
from .expressions import *
from .face import *
from .helpers import *
from .rig import *
from .scene import *

__all__ = [name for name in globals() if not name.startswith("_")]
