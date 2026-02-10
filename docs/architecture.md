## Lawkhai Aerovision – System Architecture (Phase 1 & 1.5)

### 1. Project overview

Lawkhai Aerovision is an educational AI system designed to support **aircraft maintenance technician (AMT / AME) training**.  
The system provides **conceptual explanations** of aircraft systems and **visual annotations** over curated training media.

The project is explicitly constrained to:

- **Educational and training use only**.
- **No step‑by‑step maintenance instructions**.
- **No real aircraft diagnostics or troubleshooting advice**.
- **No procedural language** (e.g., remove, install, torque, replace).
- **Consistent redirection** to approved manuals, regulatory guidance, and instructors.

The initial focus is on:

- **Electrical power generation and distribution**.
- **Hydraulic system conceptual flow**.

### 2. High-level component diagram

At a high level, Lawkhai Aerovision consists of four main subsystems:

1. **Backend core**
   - RAG (Retrieval‑Augmented Generation) engine.
   - AI tutor orchestration.
   - Safety and compliance layer.
2. **Visual intelligence**
   - Image and video annotation utilities.
   - Optional component detection (YOLO‑based).
3. **User interface**
   - Gradio web UI for text‑based conceptual Q&A.
4. **Documentation and configuration**
   - Explicit safety boundaries and configuration files.

These subsystems communicate through **stable, internal interfaces** that are independent of any one machine‑learning library or model vendor.

### 3. Backend core

#### 3.1 RAG engine

The **RAG engine** (see `backend/rag_engine.py`) is responsible for:

- Ingesting curated training materials from `/data`:
  - Text and markdown documents.
  - PDFs and images as high‑level “resource references” (not raw OCR output at this stage).
- Performing simple retrieval over this corpus, currently using:
  - File‑level and keyword‑based matching.
  - A transparent in‑memory representation (`RetrievedChunk`).
- Synthesizing a **conceptual explanation** that:
  - Focuses on system architecture, flows, and fault logic.
  - Is independent from any operational or procedural guidance.

The RAG engine is intentionally implemented as a **framework‑agnostic abstraction**. In later phases it can be backed by a forked or vendorized RAG framework (e.g., LlamaIndex or LangChain) without changing the rest of the codebase.

#### 3.2 AI tutor orchestration

The **AI tutor** (see `backend/ai_tutor.py`) orchestrates conceptual Q&A:

- Accepts a learner’s question and a **system focus**:
  - `"electrical"` or `"hydraulic"`.
- Calls the RAG engine to obtain a draft explanation grounded in training materials.
- Passes this draft through the **safety filter** to enforce training‑only rules.
- Returns a structured response (`TutorResponse`) with:
  - The final, safety‑filtered explanation.
  - The system focus.
  - The safety category (conceptual / procedural / ambiguous).
  - A flag indicating whether the original response was overridden.

This layered architecture ensures that content generation and safety enforcement are clearly separated, which is essential for auditability.

#### 3.3 Safety and compliance layer

The **safety filter** (`backend/safety_filter.py`) and **compliance logger** (`backend/compliance_logger.py`) form the core of the risk‑mitigation strategy:

- **Safety filter**:
  - Classifies queries as **conceptual**, **procedural**, or **ambiguous** using conservative heuristics.
  - Blocks or redirects any query that appears task‑based or diagnostic.
  - Generates alternative responses that:
    - Emphasise conceptual understanding.
    - Explicitly instruct users to consult official documentation and supervision.
  - Appends **training‑only disclaimers** even to acceptable conceptual answers.
- **Compliance logger**:
  - Records blocked / redirected queries as **minimal JSONL events**.
  - Avoids storing raw user text by default; uses a salted hash fingerprint instead.
  - Supports offline review for educators and safety officers.

This layer is central to aligning the system with **aviation safety culture** and regulatory expectations.

### 4. Visual intelligence

#### 4.1 Image and video annotation

The **visual annotation engine** (Phase 1.5) is implemented in:

- `vision/image_annotator.py`
- `vision/video_annotator.py`
- `vision/component_labels.yaml`

Key design points:

- An **image annotator** draws conceptual overlays on training images:
  - Bounding boxes and labels for components such as generators, buses, pumps, and actuators.
  - Descriptions sourced from `component_labels.yaml`, which stores **high‑level component roles**.
- A **video annotator** processes pre‑recorded videos:
  - Reads frames using OpenCV.
  - Applies the same conceptual overlays on selected frames.
  - Produces an annotated video for classroom use or self‑study.

In both cases, the overlays are designed strictly for **visual system understanding**, not for guiding physical interactions with aircraft.

#### 4.2 Optional YOLO integration

The **YOLO component detector** (`vision/models/yolo/detector.py`) is an **optional, plugin‑style module**:

- If available, it can detect components in training images and videos.
- Detected objects are translated into generic `ComponentDetection` instances used by the image annotator.
- If the YOLO package or model file is missing, the detector simply returns no detections and the visual pipeline continues to work with manually defined overlays.

This approach maintains a clear separation between:

- Core educational logic, which is stable and reviewable.
- Optional computer vision enhancements, which can be updated or removed without architectural changes.

### 5. User interface

The Phase 1 **Gradio UI** (`ui/interface.py`) provides:

- A **persistent safety banner** describing the training‑only scope.
- A **system selection dropdown** (Electrical / Hydraulic).
- A text box for conceptual questions.
- Outputs for:
  - The tutor’s explanation (already safety‑filtered).
  - Metadata describing how the question was categorised and whether it was redirected.

The UI does not allow uploading operational aircraft data, and it does not expose any functions that would enable real‑time diagnostics.

### 6. Configuration and extensibility

The `backend/config.py` module centralises configuration:

- Paths for training data, indexes, and logs.
- Safety and compliance settings (blocked verbs, strict mode, logging behaviour).
- Optional salts and toggles for privacy‑preserving logging.

This design allows:

- Transparent inspection by educators and regulators.
- Controlled tightening or relaxing of safety thresholds under institutional oversight.

### 7. Summary

Lawkhai Aerovision’s architecture is intentionally:

- **Layered**: clear boundaries between retrieval, safety, visualisation, and UI.
- **Auditable**: safety logic and configuration are explicit and easy to review.
- **Conservative**: any ambiguity in user intent results in conservative, training‑only responses.
- **Extensible**: RAG frameworks and vision models can be improved or swapped without destabilising the safety envelope.

