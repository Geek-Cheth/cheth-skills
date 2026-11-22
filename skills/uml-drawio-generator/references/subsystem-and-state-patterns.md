# System Overview (Subsystems) & State Machine Patterns

This reference covers the two architectural/structural diagram types that complement Swimlane Activity Diagrams inside a complete `.drawio` system package.

---

## Part 1: System Overview & Subsystems Architecture Diagram

Use this diagram as **Tab 1** when documenting a multi-subsystem system or application architecture.

### Strict Exclusions
- **NO IMAGES**: Never embed `shape=image`, base64 `image=data:...`, external URLs, phone bezels, camera notches, or browser screenshot boxes.
- Represent every user client (Mobile App, Web Portal, CLI, API Consumer, Scheduled Worker) as a clean, labeled vector rounded rectangle!

### 4-Column Left-to-Right Layout Blueprint

Place everything inside the outer `shape=umlFrame` (`x="20" y="20"`, `container=0`, all cells under `parent="1"` for global waypoint precision):

| Column | X Range (Typical) | Elements | Style / Notes |
| :--- | :--- | :--- | :--- |
| **Col 1: Entry & Clients** | `x = 60..520` | `40x40` black Start circle (`x=60`) → Client/Actor rounded rectangles (`width=320`, `height=110–140`, `x=200`) | Label each client with bold name + actor roles (e.g., `<b>Staff Mobile App</b><br><br>Roles: End User, Operator, Supplier`). Stack multiple clients vertically with `>= 120px` gap. |
| **Col 2: Diamond Routing Bus** | `x = 660..960` | Cascading `40x40` `rhombus` diamonds | One vertical cascade bus per client (offset buses by `80–100px` horizontally, e.g., Bus 1 at `x=880`, Bus 2 at `x=760`). Entry diamond may carry a short step number (`1`); cascade splitters stay empty (`value=""`). Max 3 outgoing edges per diamond! |
| **Col 3: Core Subsystems** | `x = 1220..1660` | Vertically stacked `shape=mxgraph.uml25.behaviorAction` blocks (`width=440`, `height=130–150`, vertical gap `40px`) | Format: `<b>N. Subsystem Name</b><br><br>• Bullet 1<br>• Bullet 2<br>• Bullet 3`. Highlight the primary Auth / Security / Core Gateway subsystem (`1. ...`) with `fillColor=#fad9d5;strokeColor=#ae4132;`; keep other subsystems `#ffffff` / `#000000`. |
| **Col 4: External Services & End** | `x = 1960..2600` | Optional rounded backdrop (`fillColor=#fad9d5;strokeColor=#ae4132;`), External Service / Persistence `behaviorAction` blocks (`width=460`), and `40x40` `sumEllipse` End node (`x=2540`) | Make a shared Database / Persistence block tall enough to span vertically alongside every subsystem that writes to or reads from it! |

### Port Distribution on Tall Shared Persistence Blocks
When multiple subsystems (e.g., Subsystems 2, 3, 4, 5, 6) connect horizontally into a single tall Database block (e.g., `y=300, height=780`):
- Compute each edge's exact aligned `entryY` on the Database's left face (`entryX=0`):
  ```text
  entryY = clamp((subsystem_center_y - db_y) / db_height, 0.05, 0.95)
  ```
- Result: Perfectly straight, parallel horizontal arrows with **zero crossings**, **zero bends**, and **strictly unique entry ports**!
- If a lower subsystem (below the Database bottom) also writes to the Database, route its arrow out of `exitX=1;exitY=0.2` through a dedicated vertical corridor (e.g., `x=1840`, next one at `x=1880` — `40px` apart!) up to an unused `entryY` near the bottom of the Database's left face (`0.92`, `0.96`).

### Subsystem Flow Numbering Convention
- Entry launch: `0.1 Launch <App>`
- Session / Auth routing: `1.1 <Client A> Session`, `1.2 <Client B> Session`, `1.3 Authenticate <Client>`, `1.4 Verify Token & Roles`
- Per-subsystem flows: `N.1 <Client-to-Subsystem Action>`, `N.2 <Subsystem-to-External Action>`, `N.3 <Secondary External Action>`
- Final sync / completion to `sumEllipse`: `N.k Real-time state synced` / `Process complete`

### Subsystem-to-Activity Traceability
When generating a multi-tab `.drawio` package for a system:
- Tab 1 (`System Overview & Subsystems`) maps all `1..N` subsystems.
- Tabs `2..M` provide the detailed **Swimlane UML Activity Diagrams** implementing each subsystem's key user/system workflows, using consistent subsystem numbers or task names in each tab's `umlFrame` title!

---

## Part 2: UML State Machine Diagram

Use this diagram for an entity with a well-defined finite lifecycle (e.g., Order, Booking, Ticket, Payment, Approval Request).

### Structure
- **Outer UML Frame**: `shape=umlFrame` at `x="20" y="20"`, `container=0`, title `<Entity> Status States`.
- **No Swimlanes**: All states, start/end nodes, notes, and transitions sit directly under `parent="1"`.
- **Initial State**: `40x40` solid black circle (`ellipse;aspect=fixed;fillColor=#000000;strokeColor=#000000;`) centered at top (`y="100"`).
- **State Boxes**: Rounded rectangles (`rounded=1;arcSize=30;`), `width="240"`, `height="60"` or `80`, **UPPERCASE** state name (e.g., `DRAFT`, `SUBMITTED`, `BOOKED`, `CANCELLED`, `COMPLETED`).
- **Terminal State End Nodes**: `40x40` `sumEllipse` directly below each terminal state (`y = state_y + state_h + 80`).
- **Transitions**: Open-arrow orthogonal edges (`endArrow=open;endFill=0;jumpStyle=arc;jumpSize=8;`) labeled in standard UML transition notation:
  ```text
  triggerEvent [guard condition] /
  effect or atomic action
  ```
- **Self-Loops**: Exit one side (e.g., `exitX=1;exitY=0.5`), loop cleanly via 3 explicit waypoints (`+80px` out, `-80px` up, back over target port), and re-enter a **different** port (e.g., `entryX=0.75;entryY=0`) so exit and entry NEVER collide!
- **Side-Gutter Notes**: Place `shape=note2` (`width="320"`) in the left gutter (`x="40"`) and right gutter (`x = rightmost_state_right + 80`) explaining transition invariants, atomicity, and audit/pricing rules.
