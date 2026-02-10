## Lawkhai Aerovision – Phase 1 Implementation (AI Tutor Core)

### 1. Phase 1 objectives

Phase 1 delivers a **conceptual AI tutor** focused on:

- **Electrical power generation and distribution**.
- **Hydraulic system conceptual flow**.

The tutor:

- Answers **conceptual questions** only.
- Emphasises **system architecture, flows, and fault logic**.
- Enforces strict **non‑procedural, training‑only** boundaries.

### 2. Core modules

#### 2.1 Configuration (`backend/config.py`)

This module centralises configuration for:

- **RAG settings**:
  - Data directory (default: `data/`).
  - Index directory (default: `indexes/`).
  - Placeholder embedding model name (for potential future use).
  - Chunking parameters for text ingestion.
- **Safety settings**:
  - List of **blocked verbs** associated with procedural tasks (e.g., remove, install, torque, replace).
  - A strict‑mode toggle to enforce conservative behaviour.
- **Compliance settings**:
  - Whether compliance logging is enabled.
  - Log paths for JSONL output.
  - Salts and toggles controlling privacy behaviour.

By collecting these settings in one place, the system remains **transparent and reviewable**.

#### 2.2 RAG engine (`backend/rag_engine.py`)

The RAG engine is a **minimal retrieval and synthesis layer**:

- Ingests training resources from `data/`:
  - Text and markdown files are indexed directly.
  - PDFs and images are currently represented as textual stubs referencing their educational contents.
- Performs simple **keyword‑based retrieval**:
  - Scores documents based on overlap between the learner’s question and document content.
  - Can be replaced later by a vector‑based index without changing the public API.
- Synthesises a **high‑level explanation**:
  - Introduces the selected system (electrical/hydraulic) at a conceptual level.
  - Lists relevant training resources and encourages thinking in terms of:
    - Power or pressure sources.
    - Distribution paths and protection.
    - Dependent loads or actuators.

This implementation is intentionally light‑weight, allowing instructors and reviewers to understand exactly how answers are constructed.

#### 2.3 Safety filter (`backend/safety_filter.py`)

The safety filter enforces core project constraints:

- **Classification**:
  - Uses keyword and pattern heuristics to label queries as:
    - `conceptual` (e.g., “how does the main AC bus work?”).
    - `procedural` (e.g., “how to replace the generator?”, “what steps do I follow?”).
    - `ambiguous` when intent is unclear.
- **Policy application**:
  - For procedural or ambiguous queries:
    - Suppresses any model‑generated answer.
    - Returns a carefully worded message explaining:
      - The training‑only scope of Lawkhai Aerovision.
      - The need to consult approved manuals and instructors.
      - How to rephrase the question conceptually.
  - For conceptual queries:
    - Passes the RAG‑generated answer through, adding a **standard disclaimer**.

This layer is central to the system’s alignment with aviation safety culture.

#### 2.4 Compliance logger (`backend/compliance_logger.py`)

The compliance logger provides **auditability** without compromising privacy:

- Records only **blocked or redirected** queries.
- Stores:
  - UTC timestamp.
  - Safety category.
  - Reason codes (e.g., blocked verbs, stepwise language).
  - System focus (electrical/hydraulic).
  - A salted hash fingerprint of the query and its length.
- Avoids storing raw query text by default.

These logs allow safety and academic staff to monitor usage trends and verify that the safety mechanisms are working as intended.

#### 2.5 AI tutor orchestration (`backend/ai_tutor.py`)

The AI tutor provides a unified interface for answering conceptual questions:

- `AiTutor.answer_conceptual_question(question, system_focus)`:
  - Calls the RAG engine for a draft explanation.
  - Passes the draft through the safety filter.
  - Returns a structured `TutorResponse` containing:
    - The final answer (potentially redirected).
    - The chosen system focus.
    - The safety category.
    - A flag indicating whether the query was blocked or redirected.

This orchestration layer is what the user interface and any future API should call.

#### 2.6 Backend demo entry point (`backend/app.py`)

For simple command‑line testing, `backend/app.py` provides:

- A `run_demo()` function that:
  - Prompts the user for a conceptual question about the electrical system.
  - Displays the AI tutor’s response and safety metadata.

This demo is useful for **manual verification** by educators and reviewers.

### 3. User interface (`ui/interface.py`)

The Phase 1 Gradio interface exposes the AI tutor in a controlled way:

- A **persistent safety banner** summarising:
  - Training‑only purpose.
  - Prohibition on procedures and diagnostics.
  - Requirement to consult AMM and instructors.
- A **system selection dropdown**:
  - Electrical power generation & distribution.
  - Hydraulic system conceptual flow.
- A text box for learner queries.
- Outputs:
  - The safety‑filtered explanation.
  - Metadata describing safety classification and any redirection.

The interface is deliberately minimal and professional in tone, suitable for use in a classroom or supervised lab.

### 4. Data curation

Training content ingested into `/data` should be:

- Limited to **system descriptions, diagrams, and explanatory text**.
- Screened to exclude:
  - AMM task cards and job‑step procedures.
  - Torque tables and detailed adjustment instructions.
  - Customer‑specific work instructions.

Data curation is a critical institutional responsibility and complements the in‑software safety measures.

### 5. Extensibility and future work

Future Phase 1+ work can build upon this foundation by:

- Replacing the simple RAG engine with a more advanced, vector‑based system.
- Adding richer citation support and diagram references.
- Extending the domain model to other systems, such as:
  - Pneumatics.
  - Environmental control.
  - Landing gear and brake systems (conceptually).

Any such extensions should maintain:

- Clear separation between **conceptual explanations** and **operational guidance**.
- Strong safety filtering.
- Transparent, reviewable behaviour suitable for academic and regulatory scrutiny.

