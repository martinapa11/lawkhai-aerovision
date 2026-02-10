"""
YOLOv8-based component detection (optional, training-only).

Constraints
-----------
- Training data only; no operational or live aircraft feeds.
- Detection is limited to a predefined set of components
  (e.g., generator, pump, bus bar) for educational visualisation.
- The entire module is optional and can be disabled by:
  * Not installing the `ultralytics` package, or
  * Not providing a model path, or
  * Setting `enabled=False` when constructing the detector.

Integration strategy
--------------------
- This module translates YOLO predictions into the generic
  `ComponentDetection` objects used by `vision.image_annotator`.
- The rest of the system depends only on the abstract detector
  function, not on YOLO specifics.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from vision.image_annotator import ComponentDetection


try:
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover - graceful fallback
    YOLO = None  # type: ignore[misc,assignment]


@dataclass
class YoloConfig:
    """
    Configuration for the YOLO component detector.

    - model_path: path to a trained YOLOv8 model (training-only data).
    - class_to_component: mapping from YOLO class names/ids to
      Lawkhai Aerovision component IDs (e.g. GENERATOR, PUMP).
    """

    model_path: Path
    class_to_component: Dict[str, str]


class YoloComponentDetector:
    """
    Thin wrapper around a YOLOv8 model for component detection.

    This detector is intentionally conservative and optional:
    - If YOLO is unavailable or the model file is missing, `enabled`
      will be False and `__call__` will yield no detections.
    - Callers should *not* rely on this for any operational purpose;
      it exists purely to support visual learning in training media.
    """

    def __init__(self, config: YoloConfig, *, enabled: Optional[bool] = None) -> None:
        self.config = config
        self._model = None

        # Determine whether the detector is active.
        if enabled is not None:
            self.enabled: bool = enabled
        else:
            self.enabled = YOLO is not None and self.config.model_path.is_file()

        if self.enabled and YOLO is not None:
            self._model = YOLO(str(self.config.model_path))

    def __call__(self, image: np.ndarray) -> Iterable[ComponentDetection]:
        """
        Run detection on a BGR image and yield component detections.
        """

        if not self.enabled or self._model is None:
            return []

        # YOLO expects RGB; OpenCV uses BGR.
        rgb = image[:, :, ::-1]
        results = self._model(rgb, verbose=False)

        detections: List[ComponentDetection] = []
        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            for box in boxes:
                cls_idx = int(box.cls[0])
                score = float(box.conf[0])
                # Map class index or name to a conceptual component ID.
                class_name = self._resolve_class_name(result, cls_idx)
                comp_id = self.config.class_to_component.get(class_name)
                if not comp_id:
                    continue

                x_min, y_min, x_max, y_max = map(int, box.xyxy[0].tolist())
                detections.append(
                    ComponentDetection(
                        component_id=comp_id,
                        bbox=(x_min, y_min, x_max, y_max),
                        score=score,
                    )
                )

        return detections

    @staticmethod
    def _resolve_class_name(result, cls_idx: int) -> str:
        """
        Resolve a YOLO class index to its name string.
        """

        names = getattr(result, "names", None)
        if isinstance(names, dict):
            return str(names.get(cls_idx, cls_idx))
        return str(cls_idx)


__all__ = ["YoloComponentDetector", "YoloConfig"]

