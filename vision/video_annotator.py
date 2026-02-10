"""
Video annotation utilities for Lawkhai Aerovision (Phase 1.5).

Scope
-----
- Open pre-recorded training videos of aircraft systems.
- Sample frames, apply image-level annotations, and write out
  annotated videos or individual frames.
- Provide a clear separation between:
  * Generic OpenCV video I/O.
  * Conceptual overlays supplied by ImageAnnotator or similar tools.

Constraints
-----------
- No live camera integration for operational aircraft.
- Training videos only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np


FrameAnnotatorFn = Callable[[np.ndarray], np.ndarray]


class VideoAnnotator:
    """
    Simple wrapper around OpenCV video reading/writing for training content.

    The heavy lifting of drawing conceptual overlays is delegated to a
    frame annotator function, typically using ImageAnnotator.
    """

    def __init__(self, frame_annotator: FrameAnnotatorFn) -> None:
        self.frame_annotator = frame_annotator

    def annotate_video(
        self,
        input_path: Path,
        output_path: Path,
        *,
        sample_every_n_frames: int = 1,
        max_frames: Optional[int] = None,
    ) -> None:
        """
        Read a training video, annotate frames, and write out a new video.

        Parameters
        ----------
        input_path:
            Path to a pre-recorded training video (no live feeds).
        output_path:
            Path for the annotated output video.
        sample_every_n_frames:
            Process every Nth frame to reduce compute cost if needed.
        max_frames:
            Optional cap on number of frames to process, for short demos.
        """

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {input_path}")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        frame_index = 0
        processed_frames = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % sample_every_n_frames == 0:
                    annotated = self.frame_annotator(frame)
                else:
                    # Pass-through for skipped frames to keep timing consistent.
                    annotated = frame

                writer.write(annotated)

                frame_index += 1
                processed_frames += 1
                if max_frames is not None and processed_frames >= max_frames:
                    break
        finally:
            cap.release()
            writer.release()


__all__ = ["VideoAnnotator", "FrameAnnotatorFn"]

