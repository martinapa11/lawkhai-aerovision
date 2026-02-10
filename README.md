## Lawkhai Aerovision

AI-assisted **visual learning system** for aircraft maintenance training, with an initial focus on:

- **Electrical power generation and distribution**
- **Hydraulic system conceptual flow**

Lawkhai Aerovision is designed for **AMT/AME students** and instructors.  
It provides **conceptual explanations** and **visual annotations** of aircraft systems, strictly for **educational use**.

### Safety and scope (critical)

- **Training and education only** – not for operational use.
- **No step-by-step maintenance instructions.**
- **No real aircraft diagnostics or troubleshooting guidance.**
- Avoids procedural verbs such as *remove, install, torque, replace, repair, fix*.
- Explicitly redirects learners to:
  - Approved **Aircraft Maintenance Manuals (AMM)**.
  - Type-specific documentation.
  - Qualified instructors and supervisors.

This project is designed to align with aviation safety culture and regulatory expectations (e.g. Transport Canada style training standards).

### Repository layout

- `backend/`
  - `config.py` – central configuration (RAG, safety, compliance).
  - `rag_engine.py` – simple RAG abstraction over `/data` training material.
  - `ai_tutor.py` – orchestrates conceptual Q&A for electrical/hydraulic systems.
  - `safety_filter.py` – enforces training-only scope and blocks procedural queries.
  - `compliance_logger.py` – privacy-preserving JSONL logging of blocked queries.
  - `app.py` – small CLI demo entry point.
- `ui/`
  - `interface.py` – Gradio UI with system dropdown and persistent safety banner.
- `vision/`
  - `component_labels.yaml` – conceptual component metadata (generator, pump, buses, etc.).
  - `image_annotator.py` – draws labeled boxes on training images (OpenCV).
  - `video_annotator.py` – annotates pre-recorded training videos.
  - `models/yolo/` – optional YOLOv8-based detector (plugin-style, can be disabled).
- `docs/`
  - `architecture.md` – system architecture overview.
  - `safety-boundaries.md` – formal safety and scope definition.
  - `phase1-implementation.md` – details of the AI tutor core.
  - `phase1_5-visual-intelligence.md` – details of the visual subsystem.
- `examples/`
  - `demo_walkthrough.md` – example learning session focused on electrical power distribution.
- `data/`
  - (to be created by you) curated training documents, diagrams, and PDFs.
- `logs/`
  - (created at runtime) compliance logs for blocked / redirected queries.

### Getting started

#### 1. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
.\.venv\Scripts\activate  # on Windows PowerShell
```

#### 2. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

For optional YOLO-based detection, also install:

```bash
pip install ultralytics
```

> YOLO is not required to use the AI tutor or basic visual annotations.

#### 3. Add training data

Create a `data/` directory at the project root and add **curated training materials**, such as:

- System description PDFs.
- Text/markdown summaries of electrical and hydraulic systems.
- Training schematics or non-sensitive diagrams.

Avoid including:

- AMM task cards or job-step procedures.
- Torque tables and adjustment instructions.
- Customer-specific work instructions.

#### 4. Run the Phase 1 tutor UI (Gradio)

From the project root:

```bash
python -m ui.interface
```

Then open the URL printed by Gradio (typically `http://127.0.0.1:7860`) in a browser.

You should see:

- A safety banner at the top.
- A system selector (Electrical / Hydraulic).
- A text box to ask conceptual questions about system behaviour.

#### 5. (Optional) Run the backend demo

For a simple command-line test:

```bash
python -m backend.app
```

This will prompt for a conceptual question about the electrical system and print the AI tutor’s answer plus safety metadata.

### Notes on data privacy and logging

- The compliance logger stores **only minimal, privacy-conscious records**:
  - Timestamps, safety categories, reason codes, and salted fingerprints of queries.
  - Raw user text is **not stored by default**.
- You can review `logs/blocked_queries.jsonl` (if enabled) to understand:
  - How often learners ask procedural or ambiguous questions.
  - Whether additional training or onboarding is needed.

### Extending the project

Future enhancements can include:

- Swapping the simple RAG engine for a more advanced framework (e.g. LlamaIndex or LangChain) behind the same `RagEngine` interface.
- Richer citation and diagram support in answers.
- Additional system domains (pneumatics, ECS, landing gear, etc.), still at a **conceptual** level.

Any extension should maintain the core principles:

- **Safety first.**
- **Training only.**
- **No procedural guidance or diagnostics.**

