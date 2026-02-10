## Lawkhai Aerovision – Safety Boundaries and Use Limitations

### 1. Purpose of this document

This document formally describes the **safety boundaries** of Lawkhai Aerovision, an AI‑assisted learning tool for aircraft maintenance training.  
It is intended to be read by:

- Academic supervisors and curriculum designers.
- Safety and compliance officers.
- Immigration and regulatory reviewers evaluating the project’s risk posture.

### 2. Intended use

Lawkhai Aerovision is designed for **classroom and self‑study environments** where learners are developing:

- Conceptual understanding of aircraft systems.
- Intuition for cause–effect relationships and fault logic.
- Familiarity with high‑level system architectures and component roles.

The system’s primary functions are:

- To answer **conceptual questions** about:
  - How electrical power generation and distribution is organised.
  - How hydraulic systems move and control pressure.
- To provide **visual overlays** on training images and videos that:
  - Highlight major components.
  - Indicate nominal flow paths.
  - Reinforce system‑level reasoning, not actions.

### 3. Explicit non-goals (what the system does not do)

Lawkhai Aerovision is *not* intended for, and is explicitly constrained against:

- Providing **step‑by‑step maintenance instructions** of any kind.
- Suggesting or validating **torque values, clearances, or adjustment settings**.
- Recommending specific **maintenance actions** (e.g., removal, installation, replacement, repair).
- Performing **real‑time or post‑event diagnostics** on operational aircraft.
- Serving as a **source of operational advice** for any certificated maintenance activity.

The system is not certified as, and must never be regarded as:

- An Aircraft Maintenance Manual (AMM) or any form of official documentation.
- A Computerised Maintenance Management System (CMMS).
- A fault isolation manual (FIM) or fault interpretation expert system.

### 4. Safety mechanisms in software design

Several architectural features enforce these boundaries.

#### 4.1 Safety filter

The **safety filter** (`backend/safety_filter.py`) is the primary control mechanism:

- **Intent classification**:
  - Queries are classified as **conceptual**, **procedural**, or **ambiguous**.
  - Phrases such as “how to”, “steps”, “procedure”, “checklist”, “what should I do”, and specific verbs like “remove”, “install”, “torque”, “replace”, “repair” are treated as indicators of procedural intent.
- **Blocking and redirection**:
  - Queries classified as procedural or ambiguous are **not answered directly**.
  - Instead, users receive a message that:
    - Explains the training‑only role of the system.
    - Directs them to the **approved AMM**, regulatory documentation, and qualified supervision.
    - Suggests how to rephrase the question towards conceptual understanding.
- **Disclaimers**:
  - Even for acceptable conceptual queries, the system appends a concise disclaimer:
    - Clarifying that the explanation is for **education only**.
    - Stating that it cannot replace official manuals or regulated training.

This conservative stance aligns with aviation safety culture, where ambiguity is resolved by **erring on the side of caution**.

#### 4.2 Compliance logging

The **compliance logger** (`backend/compliance_logger.py`) records **blocked or redirected queries** for offline review:

- Uses a **privacy‑preserving JSONL format**:
  - No raw query text stored by default.
  - Queries represented by a salted SHA‑256 fingerprint and length.
  - Optional query previews are disabled by default and can remain off in most deployments.
- Captures:
  - Timestamp (UTC).
  - Safety category (procedural / ambiguous).
  - Reason codes (e.g., “blocked_verbs:remove,replace”, “task_how_to_language”).
  - High‑level system context (electrical/hydraulic).

These logs support:

- Safety audits and curriculum refinement.
- Empirical monitoring of how learners interact with the system.
- Early detection of usage patterns that might drift towards operational tasks.

#### 4.3 Visual annotation constraints

The visual subsystem, by design:

- Operates only on **pre‑recorded, training‑oriented media**:
  - No live camera or aircraft data feed interfaces.
- Annotates images and videos with:
  - Component labels.
  - Conceptual descriptions of **roles and relationships**, not actions.
- When YOLO or other detectors are used:
  - Models are trained on curated, non‑operational data.
  - Outputs are mapped to **component IDs** (e.g., GENERATOR, PUMP) used solely for visual highlighting.

This ensures that visual outputs function as **didactic illustrations**, not inspection or diagnostic tools.

### 5. Alignment with aviation training standards

Although Lawkhai Aerovision is not itself a certified training program, its design is informed by:

- The safety culture embodied in regulations and guidance from authorities such as **Transport Canada** and other national aviation authorities.
- The principle that **approved maintenance manuals and type‑specific training** remain the primary source of guidance for any maintenance action.
- The expectation that learners work under **qualified supervision** and follow **documented procedures**.

The system supports these principles by:

- Reinforcing system‑level reasoning that underpins formal training curricula.
- Emphasising that any real‑world task must refer back to official documents.
- Avoiding language that might be misconstrued as an instruction or approval.

### 6. User responsibilities and institutional controls

Institutions deploying Lawkhai Aerovision should:

- Present it explicitly as a **supplementary learning tool**, not a replacement for lectures, labs, or manuals.
- Ensure that students understand:
  - The system does not authorise or validate maintenance actions.
  - They must always defer to **current approved documentation** and **instructor guidance**.
- Periodically review:
  - Compliance logs for emerging risk patterns.
  - Training materials ingested into the RAG corpus to confirm that:
    - Stepwise procedures and job cards are excluded or heavily filtered.
    - Content remains aligned with the intended educational objectives.

### 7. Summary

In summary, Lawkhai Aerovision is positioned as a **safety‑conscious educational tool** that:

- Limits itself to conceptual explanations and visual aids.
- Implements multiple software controls to prevent procedural use.
- Provides traceability through privacy‑respecting logging.
- Encourages adherence to aviation regulations and institutional training standards.

These measures collectively help ensure that the project supports, rather than undermines, **aviation safety and regulatory compliance**.

