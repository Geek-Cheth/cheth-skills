---
name: uml-drawio-generator
description: >-
  Generate clean, standardized UML diagrams in Draw.io (.drawio / mxfile XML) format
  from any system specification, codebase, architecture, or workflow logic. Supports
  multi-role Swimlane UML Activity Diagrams, System Overview & Subsystems Architecture
  Diagrams, and UML State Machine Diagrams with outer UML frames, 40x40 decision/merge
  diamonds, cascading diamond fan-out/fan-in, strict unique port separation, arc line
  jumps, and zero embedded images. Use whenever the user asks to create, convert, or
  document a system or business logic as Draw.io UML diagrams.
---

# UML Draw.io Generator Skill

Generate publication-grade, uncompressed `.drawio` (`<mxfile>`) XML diagrams from any system description, codebase, or workflow specification.

## Supported Diagram Types

A single `.drawio` file may contain one `<diagram>` tab or multiple `<diagram>` tabs covering the full system:

1. **System Overview & Subsystems** — Left-to-right layered architecture: Start node → Client/Actor Entry Blocks → Cascading `40x40` Routing Diamonds → Core Subsystems (`shape=mxgraph.uml25.behaviorAction`) → External Services & Persistence → End node.
2. **Swimlane UML Activity Diagram** — Top-to-bottom workflow partitioned into explicit vertical role swimlanes (`User`, `Admin`, `System`, `Worker`, `External Gateway`, etc. — 2 to N roles) with `40x40` decision/merge diamonds, bracketed `[guard]` conditions, and side-gutter UML notes.
3. **UML State Machine Diagram** — Lifecycle states (`UPPERCASE`) inside an outer UML frame with `trigger [guard] / effect` transitions, self-loops, terminal states, and side-gutter UML notes.

## Non-Negotiable Format & Layout Rules

Every generated `.drawio` file MUST obey these rules without exception:

1. **Outer UML Frame Required**: Every `<diagram>` tab MUST have an outer `shape=umlFrame` at `x="20" y="20"` enclosing all lanes, subsystems, notes, and routing corridors with at least `20–30px` inner margin.
2. **Clear Roles (Swimlanes)**: Every Activity Diagram MUST partition actions into vertical `swimlane` columns (e.g., `User` and `System`, or 3+ roles when multiple actors/services participate). All swimlanes sit flush side-by-side at `y="80"` with identical `height`.
3. **No Images — Ever**: NEVER emit `shape=image`, `image=data:...`, external image URLs, or screenshot/device-mockup placeholders. Represent client applications and portals with clean vector rounded rectangles and text labels.
4. **Standard `40x40` Diamonds**: Every decision, merge, and routing `rhombus` MUST be exactly `width="40" height="40"`.
   - In Activity Diagrams, diamonds are **always empty** (`value=""`). Put conditions strictly on outgoing edges as `[bracketed guards]`.
   - In System Overview Diagrams, primary entry routing diamonds may optionally hold a short step index (e.g., `1`); cascading splitter diamonds stay empty (`value=""`).
5. **Never Share Connection Anchor Points (Unique Ports)**: Every edge MUST declare explicit `exitX`, `exitY`, `entryX`, `entryY`, `exitDx=0`, `exitDy=0`, `entryDx=0`, `entryDy=0`, `exitPerimeter=0`, `entryPerimeter=0`. **No two edges may attach to the exact same `(node, x, y)` point** (neither two incoming, two outgoing, nor incoming+outgoing). Spread multiple connections onto distinct coordinates (e.g., `0.25` / `0.75`, `0.2` / `0.5` / `0.8`, or evenly spaced along tall blocks).
6. **Use a Separate Diamond When Fan-Out or Fan-In Exceeds Capacity**:
   - A `40x40` diamond has only 4 cardinal vertices: Top `(0.5, 0)`, Right `(1, 0.5)`, Bottom `(0.5, 1)`, Left `(0, 0.5)`.
   - Never attach more than **3 outgoing edges** (with 1 incoming) or **3 incoming edges** (with 1 outgoing) to a single diamond.
   - When routing to **4+ branches/subsystems** or merging **4+ paths**, chain a **cascade of separate `40x40` diamonds** (`d1 → d2 → d3`), peeling off or merging one branch per diamond!
   - When **2+ paths converge** onto an activity action box, prefer routing them into an explicit `40x40` **merge diamond** above the box rather than piling multiple arrows onto one side of the box.
7. **Mandatory Arc Jumps & Zero Overlapping Lines**:
   - EVERY edge (control flows, subsystem flows, state transitions, and dashed note links) MUST include `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonal=1;curved=0;orthogonalLoop=1;jettySize=24;jumpStyle=arc;jumpSize=8;`.
   - Minimize crossings through clean column ordering first; when crossings are unavoidable, `jumpStyle=arc` renders an unambiguous bridge arc.
   - Parallel edges running through the same corridor MUST use distinct `x` or `y` tracks separated by at least `30–40px` using explicit `<Array as="points"><mxPoint x="..." y="..."/></Array>` waypoints. Never let two edges overlap collinearly or cut across shapes/labels.
8. **10px Grid & Crisp Visual Hierarchy**:
   - Set `grid="1" gridSize="10"` on `<mxGraphModel>`. Align all coordinates, sizes, and waypoints to multiples of `10` (prefer `20`).
   - Monochrome precision (`#000000` stroke/text on `#ffffff` fill, `Helvetica` `14px`) for Activity and State diagrams; optional soft accent (`fillColor=#fad9d5;strokeColor=#ae4132;`) for highlighted core/auth subsystems and external-infrastructure backdrops in System Overview diagrams.
   - Output **uncompressed** `<mxfile>` XML directly so Draw.io opens it immediately and it stays inspectable and diffable.

## References & Templates

Load only the references needed for the diagrams you are producing:

- **Exact XML Styles, Dimensions & Ports**: Read [references/style-tokens.md](./references/style-tokens.md) for copy-paste style strings for frames, swimlanes, actions, `40x40` diamonds, start/end nodes, notes, subsystem blocks, and edges.
- **Diamond Cascades, Port Allocation & Zero-Overlap Routing**: Read [references/routing-and-diamonds.md](./references/routing-and-diamonds.md) before laying out any branching, looping, merging, or multi-subsystem graph.
- **System Overview (Subsystems) & State Machine Patterns**: Read [references/subsystem-and-state-patterns.md](./references/subsystem-and-state-patterns.md) when generating a System Overview & Subsystems tab or a State Machine tab.
- **Ready-to-Adapt Starters**:
  - [templates/activity-swimlane-template.drawio](./templates/activity-swimlane-template.drawio)
  - [templates/subsystem-overview-template.drawio](./templates/subsystem-overview-template.drawio)
  - [templates/state-machine-template.drawio](./templates/state-machine-template.drawio)

## Step-by-Step Generation Workflow

### Step 1: Analyze the System or Logic
From the user's prompt, specification, or codebase:
- Identify which diagram tab(s) are needed:
  - A **System Overview & Subsystems** tab when describing a full system or multi-module architecture.
  - One **Swimlane Activity Diagram** tab per distinct end-to-end user/system task or workflow.
  - One **State Machine** tab per key entity lifecycle (e.g., Order, Ticket, Job, Payment) if stateful transitions matter.
- For each Activity Diagram, list all **Roles** (e.g., `User`, `Reviewer`, `System`, `Scheduler`), every action step, every decision condition (`[guard]`), every early-exit or error branch, every merge point, and every business invariant worth capturing in a side-gutter UML Note.
- For a System Overview Diagram, list: Client/Actor Entry Points (no images!), Core Subsystems (`1..N` with 2–4 concise bullet points each), External Services / Data Stores, and numbered flows (`0.1`, `1.1`, `2.1`, ...).

### Step 2: Plan the Coordinate Grid Before Writing XML
Design coordinates on a `10px` / `20px` grid before emitting XML:
1. **Lanes (Activity)**: Place swimlanes flush side-by-side at `y="80"`. If left-gutter notes exist (`x="40"`, `width="320"`), start the first lane at `x="420"`; otherwise start at `x="40"`. Size each lane width to fit its internal action columns (`360–480` for 1 column, `640–960` for 2 columns, `1280–1480` for 3 columns).
2. **Vertical Rhythm**: Place the Start node (`40x40`) at `y="80"` inside the initiating role's lane. Maintain `60–80px` vertical clearance between stacked boxes and diamonds so vertical `[guard]` labels never collide with borders.
3. **Port Reservation Map**: Maintain a mental or scratch table of used `(node_id, port_x, port_y)` slots for every vertex. Never assign the same port twice. Whenever >3 edges leave or enter a junction, split across chained `40x40` diamonds.
4. **Routing Corridors**: Assign dedicated vertical loop-back / bypass corridors (`x` coordinates spaced by `>= 40px`) outside action columns and add explicit `<Array as="points">` waypoints on every long or cross-lane turn.
5. **Side-Gutter Notes**: Place `shape=note2` (`width="320"`) in the right gutter (`x = last_lane_right + 60`) or left gutter (`x = 40`), vertically aligned with the target node, connected by a dashed arrowless edge with `jumpStyle=arc;jumpSize=8;`.
6. **Outer Frame & Page Size**: Compute `frame` width and height so every lane, note, and waypoint sits inside `[20, 20]` to `[20 + frame_w, 20 + frame_h]` with at least `30px` bottom/right margin. Set `pageWidth` and `pageHeight` at least `80px` larger than the frame.

### Step 3: Emit Clean Uncompressed `.drawio` XML
- Use `<mxfile host="app.diagrams.net" pages="N">` wrapping one `<diagram id="..." name="...">` per tab, each containing an uncompressed `<mxGraphModel ...><root>...</root></mxGraphModel>`.
- Ensure every `id` is unique within its `<diagram>`, XML entities (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#10;`) are properly escaped, and all edges in Activity/State diagrams use `parent="1"` so waypoint coordinates are always in global canvas space.

### Step 4: Validate Automatically Before Delivery
Always run the bundled validator script on the generated `.drawio` file:

```bash
python scripts/validate_drawio.py path/to/output.drawio
```

If the validator reports **any** errors (missing `jumpStyle=arc`, port collisions, non-`40x40` diamonds, diamond degree overflow, overlapping boxes, collinear overlapping tracks, embedded images, missing `umlFrame`, or dangling IDs), fix every error and re-run until validation exits with code `0`.
