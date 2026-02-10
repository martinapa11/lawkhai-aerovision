"""
Image annotation utilities for Lawkhai Aerovision (Phase 1.5).

Scope
-----
- Load training images of aircraft systems.
- Draw conceptual overlays:
  * Bounding boxes or highlight regions for key components.
  * Text labels taken from component_labels.yaml.
  * Optional arrows to indicate nominal flow paths.
- Support an optional detection backend (e.g. YOLO) in a plugin style,
  but remain fully functional without it.

Constraints
-----------
- No real-time or live aircraft support.
- No maintenance procedures or diagnostic advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

import cv2
import numpy as np
import yaml


ComponentId = str


@dataclass
class ComponentDetection:
    """
    Conceptual representation of a detected component in an image.

    bbox is in pixel coordinates: (x_min, y_min, x_max, y_max).
    """

    component_id: ComponentId
    bbox: Tuple[int, int, int, int]
    score: float = 1.0


class ComponentCatalog:
    """
    Loads conceptual component labels from component_labels.yaml.
    """

    def __init__(self, labels_path: Path) -> None:
        self._labels = self._load(labels_path)

    @staticmethod
    def _load(path: Path) -> dict:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data or {}

    def describe(self, system: str, component_id: ComponentId) -> str:
        """
        Return a short conceptual description for a component, if available.
        """

        for item in self._labels.get(system, []):
            if item.get("id") == component_id:
                name = item.get("name", component_id)
                desc = item.get("description", "")
                return f"{name}: {desc}"
        return component_id


DetectorFn = Callable[[np.ndarray], Iterable[ComponentDetection]]


class ImageAnnotator:
    """
    High-level interface for annotating training images with conceptual labels.

    The detector is optional. If not provided, this class can still be used
    with manually defined detections or coordinates defined in lesson content.
    """

    def __init__(
        self,
        component_catalog: ComponentCatalog,
        detector: Optional[DetectorFn] = None,
    ) -> None:
        self.catalog = component_catalog
        self.detector = detector

    def annotate_image(
        self,
        image: np.ndarray,
        system: str,
        detections: Optional[List[ComponentDetection]] = None,
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels for detected components.

        Parameters
        ----------
        image:
            Input BGR image (OpenCV format).
        system:
            'electrical' or 'hydraulic' – used to fetch conceptual labels.
        detections:
            Optional pre-computed detections. If None and a detector is
            configured, the detector will be called.
        """

        if detections is None and self.detector is not None:
            detections = list(self.detector(image))
        elif detections is None:
            detections = []

        annotated = image.copy()
        for det in detections:
            x_min, y_min, x_max, y_max = det.bbox
            cv2.rectangle(annotated, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            label_text = self.catalog.describe(system, det.component_id)
            self._draw_label(annotated, label_text, (x_min, y_min - 8))

        return annotated

    @staticmethod
    def _draw_label(image: np.ndarray, text: str, origin: Tuple[int, int]) -> None:
        """
        Draw a readable label box with text.
        """

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.45
        thickness = 1

        (w, h), _ = cv2.getTextSize(text, font, scale, thickness)
        x, y = origin
        y = max(h + 4, y)

        cv2.rectangle(image, (x, y - h - 4), (x + w + 4, y + 2), (0, 0, 0), -1)
        cv2.putText(image, text, (x + 2, y - 2), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)


__all__ = ["ComponentDetection", "ComponentCatalog", "ImageAnnotator"]

