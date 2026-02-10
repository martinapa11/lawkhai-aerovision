## Lawkhai Aerovision – Phase 1.5 Visual Intelligence

### 1. Phase 1.5 objectives

Phase 1.5 extends Lawkhai Aerovision with **visual learning capabilities**:

- Annotating training images and videos.
- Highlighting major electrical and hydraulic components.
- Depicting nominal flow paths (power or pressure) at a conceptual level.

The aim is to help learners build a **mental model** of how systems are laid out and how energy or pressure moves through them, without suggesting any maintenance actions.

### 2. Design principles

The visual subsystem is designed to:

- Operate only on **pre‑recorded, curated training media**.
- Provide overlays that reflect **system understanding**, not procedures.
- Be **modular and optional**:
  - The system remains functional even if component detection models (e.g., YOLO) are absent.
  - Only high‑level component identifiers and conceptual descriptions are exposed to users.

### 3. Core components

#### 3.1 Component labels (`vision/component_labels.yaml`)

This YAML file defines:

- **Electrical components**:
  - GENERATOR, AC_BUS, TRU, DC_BUS, etc.
- **Hydraulic components**:
  - RESERVOIR, PUMP, MANIFOLD, ACTUATOR, etc.

Each entry includes:

- A stable `id` used across the visual and detection subsystems.
- A human‑readable `name`.
- A **short conceptual description** of the component’s role.

These descriptions are deliberately non‑procedural; they focus on “what this does in the system” rather than “how to work on it”.

#### 3.2 Image annotation (`vision/image_annotator.py`)

The image annotator provides:

- `ComponentDetection`:
  - Represents the presence of a component in an image by:
    - `component_id`.
    - Bounding box coordinates (in pixels).
    - Optional confidence score.
- `ComponentCatalog`:
  - Loads `component_labels.yaml`.
  - Resolves component IDs to conceptual descriptions.
- `ImageAnnotator`:
  - Accepts an optional **detector function** that returns `ComponentDetection` instances.
  - Draws bounding boxes and label boxes on images using OpenCV.
  - Uses the `ComponentCatalog` to display **training‑oriented labels**.

The annotator is agnostic to how detections are produced: they may come from an automated detector, from manual lesson authoring, or from simple coordinate lists defined in teaching materials.

#### 3.3 Video annotation (`vision/video_annotator.py`)

The video annotator is a thin wrapper around OpenCV video I/O:

- `VideoAnnotator`:
  - Accepts a **frame annotator function**, typically using `ImageAnnotator`.
  - Reads frames from a **pre‑recorded** training video.
  - Applies conceptual overlays on every Nth frame (or all frames).
  - Writes out an annotated video file for use in lectures or self‑study.

No facilities are provided for:

- Live camera capture.
- Real‑time analysis of operational aircraft.

This deliberate limitation preserves the system’s training‑only character.

### 4. Optional YOLO-based detection

#### 4.1 YOLO detector wrapper (`vision/models/yolo/detector.py`)

The YOLO integration is implemented as a **plugin‑style wrapper**:

- `YoloConfig`:
  - Specifies the path to a trained YOLO model.
  - Defines a mapping from YOLO class names/IDs to component IDs (e.g., `"generator"` → `"GENERATOR"`).
- `YoloComponentDetector`:
  - Attempts to load a YOLOv8 model from the `ultralytics` package.
  - Sets an `.enabled` flag based on whether dependencies and model files are present.
  - When called on an image, returns a list of `ComponentDetection` objects for recognised components.

If YOLO is not installed or the model path is missing, the detector:

- Automatically sets `.enabled = False`.
- Returns no detections.
- Leaves the rest of the visual pipeline fully functional, relying on manual or scripted annotations instead.

#### 4.2 Integration with image annotator

To enable automated detection in a training environment, an integrator can:

- Construct a `ComponentCatalog`.
- Configure a `YoloComponentDetector` with a **training‑only model**.
- Pass the detector to `ImageAnnotator`.

This preserves the abstraction boundary: the annotator knows only about generic component detections, not about YOLO internals.

### 5. Educational benefits

The visual intelligence layer supports educational outcomes by:

- Providing **spatial context**:
  - Learners can see how components are arranged and connected.
  - Flow arrows and labels reinforce system topology and directionality.
- Reinforcing **cause–effect reasoning**:
  - Instructors can pause annotated videos to discuss:
    - What happens if a given component becomes unavailable.
    - How redundancy routes power or pressure along alternate paths.
- Supporting **multimodal learning**:
  - Combining text‑based explanations (from the AI tutor) with visual overlays.

At all times, the overlays are framed as **illustrations** rather than instructions.

### 6. Safety and compliance considerations

The visual subsystem adheres to the same safety principles as the AI tutor:

- No visual outputs are associated with:
  - Torque values, disassembly steps, or tooling.
  - Fault codes or live sensor data.
- Any textual descriptions shown in overlays:
  - Emphasise conceptual roles.
  - Avoid recommending actions.
- In deployments where additional controls are desired:
  - Institutions can restrict which videos and images are processed.
  - Only training materials vetted by instructors should be placed in the visual pipeline.

### 7. Future enhancements

Potential extensions, still within the training‑only scope, include:

- Interactive diagrams where learners click components to see:
  - Conceptual roles.
  - Example fault scenarios (at system level).
- Time‑aligned overlays that:
  - Match specific phases of an animation to textual explanations.
- Additional system coverage, such as:
  - Pneumatics and anti‑ice systems.
  - Environmental control systems (ECS).

Any future work should continue to uphold the guiding principle that **system understanding and safety culture** are the central goals, not operational maintenance guidance.

