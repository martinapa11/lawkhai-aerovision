"""
Optional YOLO-based component detection for Lawkhai Aerovision.

This package is designed as a plugin:
- If YOLO / ultralytics is not installed or a model file is missing,
  the rest of the system continues to function using manual or
  pre-defined annotations.
- Callers should always treat this as optional and check `.enabled`
  on detector instances.
"""

from .detector import YoloComponentDetector

__all__ = ["YoloComponentDetector"]

