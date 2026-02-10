## Lawkhai Aerovision – MVP Demo Walkthrough

### Scenario overview

This walkthrough illustrates how an aircraft maintenance student can use **Lawkhai Aerovision** to deepen their understanding of an **electrical power distribution system**, while remaining strictly within **training‑only** boundaries.

The demo assumes:

- Phase 1 AI tutor and Phase 1.5 visual annotation are available.
- The Gradio UI (`ui/interface.py`) is running.
- Training materials and diagrams for electrical power systems have been ingested into `data/`.

### Step 1 – Launching the tutor

1. The student opens the Lawkhai Aerovision web interface.
2. At the top of the page, they see the **safety banner**:
   - Explaining that the system is for **education only**.
   - Stating that it does *not* provide maintenance procedures or diagnostics.
   - Reminding them to always consult the **Aircraft Maintenance Manual (AMM)** and their instructor for real maintenance work.

This immediately frames the tool as a **learning assistant**, not a maintenance aid.

### Step 2 – Selecting the system

1. The student selects **“Electrical power generation & distribution”** from the **System focus** dropdown.
2. This choice tells the AI tutor and RAG engine to prioritise:
   - Electrical system training materials.
   - Conceptual explanations involving generators, buses, and power paths.

No aircraft type or tail number is entered; the discussion remains **generic and educational**.

### Step 3 – Asking an initial conceptual question

The student types a conceptual question, for example:

> “How does the main AC bus stay powered if one generator fails?”

The tutor processes this as follows:

1. The **RAG engine** retrieves relevant training content about:
   - Main AC buses.
   - Generator sources.
   - Automatic reconfiguration or backup sources (conceptually described).
2. The **AI tutor** synthesises a high‑level explanation that might cover:
   - The idea of multiple generators feeding common buses.
   - The role of bus tie contactors or equivalent devices (described conceptually, not as components to operate).
   - How critical loads are prioritised across buses.
3. The **safety filter** confirms:
   - The question is conceptual (no “how to” or task verbs).
   - It can be answered safely, but a **training‑only disclaimer** is appended.

The student sees:

- A narrative explanation of how power can be rerouted conceptually.
- A reminder that for any specific aircraft, they must consult the approved manuals.

### Step 4 – Visual reinforcement with diagrams or videos

To reinforce the teaching, the instructor introduces a visual element:

1. A training diagram or video of the **electrical distribution system** is loaded into the visual annotation tool.
2. The **image or video annotator** overlays:
   - Labels such as “Generator”, “AC bus”, “TRU”, and “DC bus”.
   - Simple arrows indicating the **normal flow of electrical power**.

The student can now relate the textual explanation to a **spatial representation**:

- Understanding that generators feed buses.
- Recognising where TRUs convert AC to DC.
- Seeing the main and secondary paths conceptually, without any instruction on operating switches or performing maintenance.

### Step 5 – Exploring fault logic conceptually

The student asks a follow‑up question such as:

> “What happens to the DC buses if one TRU stops working?”

The system’s behaviour:

1. The tutor recognises this as a conceptual “what happens if” question.
2. The RAG engine retrieves training text discussing:
   - The relationship between TRUs and DC buses.
   - Typical redundancy or backup arrangements (concept‑level only).
3. The tutor explains, for example:
   - That loss of a TRU can reduce available DC capacity.
   - That some non‑essential loads might be shed to protect essential equipment.
   - That different aircraft designs manage these transitions in different ways.
4. The safety filter again adds a disclaimer noting that:
   - The explanation is generic and educational.
   - Actual aircraft behaviour must be verified from the **AMM and system schematics**.

If a relevant annotated diagram or video is available, the instructor can:

- Pause on a frame where the TRU and DC buses are highlighted.
- Use the overlays as a starting point for discussion:
  - “Here is where the TRU connects.”
  - “Here is the DC bus that depends on it.”

This helps the student build a **cause–effect chain** without any reference to the physical steps of troubleshooting or replacing the TRU.

### Step 6 – Demonstrating a safety redirection

For educational purposes, the instructor may show how the system responds to an **inappropriate, procedural question**.  
For instance, the student might intentionally ask:

> “What steps should I follow to replace the generator?”

In this case:

1. The safety filter:
   - Detects procedural phrasing (“steps”, “replace”).
   - Classifies the query as **procedural**.
2. The system:
   - **Does not** provide any instructions or steps.
   - Responds with a **safety redirection message** stating:
     - That Lawkhai Aerovision cannot answer maintenance procedures.
     - That the correct sources are the AMM and regulatory documentation.
     - That the student should consult their instructor or supervisor.
   - Optionally suggests how the learner might rephrase the question conceptually, e.g.:
     - “You could instead ask about how the generator is integrated into the power system or how the system is designed to respond if it becomes unavailable.”
3. A minimal, privacy‑preserving entry is written to the **compliance log** for later review.

This demonstration reinforces the system’s **safety boundaries** and helps learners understand the limits of AI assistance in aviation maintenance.

### Step 7 – Reflecting on learning outcomes

By the end of the demo session, the student should be able to:

- Describe, in general terms, how:
  - Generators feed the main AC buses.
  - TRUs derive DC power from AC sources.
  - Redundancy and load‑shedding can protect essential loads.
- Point to key components on annotated diagrams or videos and state their **conceptual roles**.
- Recognise that:
  - Lawkhai Aerovision is a **tool for understanding systems**, not a replacement for official maintenance documentation or training.
  - Any actual maintenance task requires reference to the AMM, type‑specific instructions, and guidance from qualified personnel.

### 8. Summary

This MVP walkthrough demonstrates how Lawkhai Aerovision integrates:

- A **RAG‑based conceptual tutor**.
- A **visual annotation engine** for diagrams and training videos.
- A **strong safety and compliance layer** that blocks procedural use.

Together, these elements support aviation maintenance education while respecting the **non‑negotiable safety culture and regulatory requirements** of the field.

