# Routing, Port Separation & Diamond Cascade Rules

Clean connector geometry is what separates readable engineering diagrams from tangled charts. Follow every rule in this specification strictly.

---

## 1. Standard Diamond Geometry & Semantics

- **Size**: ALWAYS `width="40" height="40"`.
- **Activity Diagrams**:
  - Diamonds are **always empty** (`value=""`).
  - **Decision diamond**: 1 incoming flow (typically Top `entryX=0.5;entryY=0`), 2–3 outgoing guarded flows (`[condition]`).
    - Happy/primary path exits **Bottom** (`exitX=0.5;exitY=1`) to continue down the main vertical spine.
    - Secondary/failure/error branch exits **Right** (`exitX=1;exitY=0.5`).
    - Alternate/loop-back/skip branch exits **Left** (`exitX=0;exitY=0.5`).
  - **Merge diamond**: 2–3 incoming flows (Top `0.5,0`, Left `0,0.5`, Right `1,0.5`) and 1 outgoing flow (Bottom `0.5,1`). Merge incoming edges are unlabeled (unless clarifying a bypass).
- **Never combine Decision + Merge on one diamond** when that would exceed 4 ports or obscure control flow. Place a merge diamond immediately above a decision diamond (`y_decision = y_merge + 40 + 80`) connected by a single short vertical arrow (e.g., `m2 → more` in a loop).

---

## 2. Never Join Multiple Lines at the Same Point (Unique Port Rule)

**Hard Rule**: Every edge MUST connect to a unique anchor point `(node_id, x, y)`. Two edges may **NEVER** share the same `(entryX, entryY)`, the same `(exitX, exitY)`, or collide (`exit` on the exact same coordinate as `entry`) on any node!

### Approved Port Slots on Rectangles (Actions, States, Subsystems)

| Side | 1 Connection | 2 Connections | 3 Connections | N Connections (Tall Block, e.g., Shared DB) |
| :--- | :--- | :--- | :--- | :--- |
| **Top** (`y=0`) | `x=0.5` | `x=0.25`, `x=0.75` | `x=0.2`, `x=0.5`, `x=0.8` | `x = (k + 0.5) / N` |
| **Bottom** (`y=1`) | `x=0.5` | `x=0.25`, `x=0.75` | `x=0.2`, `x=0.5`, `x=0.8` | `x = (k + 0.5) / N` |
| **Left** (`x=0`) | `y=0.5` | `y=0.3`, `y=0.7` (or `0.25`, `0.75`) | `y=0.2`, `y=0.5`, `y=0.8` | Align `y = (source_center_y - target_y) / target_h` |
| **Right** (`x=1`) | `y=0.5` | `y=0.3`, `y=0.7` (or `0.25`, `0.75`) | `y=0.2`, `y=0.5`, `y=0.8` | Align `y = (target_center_y - source_y) / source_h` |

Always include `exitDx=0;exitDy=0;exitPerimeter=0;entryDx=0;entryDy=0;entryPerimeter=0;` so Draw.io snaps precisely to the specified fractional port.

### Anti-Pattern vs Correct Pattern

- **WRONG**: Three bypass/cancel arrows all pointing to `target="act_return"` with `entryX=0;entryY=0.5`.
- **RIGHT (Option A — 2 inputs)**: Route the primary path into Top `(0.5, 0)` and the bypass into Left `(0, 0.5)` (or two distinct top ports `(0.25, 0)` and `(0.75, 0)`).
- **RIGHT (Option B — 3+ inputs, PREFERRED)**: Route the converging paths into a **`40x40` merge diamond** (or a **cascade of merge diamonds** if 4+ paths converge) placed above the target action, then draw **one** clean vertical arrow from the final merge diamond's Bottom `(0.5, 1)` to the action's Top `(0.5, 0)`.

---

## 3. Cascading Separate Diamonds (When Fan-Out or Fan-In > 3)

A `40x40` diamond has **only 4 cardinal tips**: `(0.5, 0)`, `(1, 0.5)`, `(0.5, 1)`, `(0, 0.5)`.
- A single **decision/router diamond** has 1 incoming port and at most **3 outgoing ports**.
- A single **merge diamond** has at most **3 incoming ports** and 1 outgoing port.

Whenever a flow needs **more than 3 branches** (fan-out) or **more than 3 converging paths** (fan-in), **NEVER** cram multiple lines onto one tip or attach lines to diagonal sides. Instead, **chain separate `40x40` diamonds**:

### Fan-Out Cascade Pattern (e.g., 1 Client → 5 Subsystems, or 4-Way Decision)

```text
Client ──▶ ◇ d1 (x=760, y=280) ──(top 0.5,0)──▶ Subsystem 1
              │ (bottom 0.5,1 -> top 0.5,0)
              ▼
           ◇ d2 (x=760, y=420) ──(right 1,0.5)──▶ Subsystem 2
              │ (bottom 0.5,1 -> top 0.5,0)
              ▼
           ◇ d3 (x=760, y=610) ──(right 1,0.5)──▶ Subsystem 3
              │ (bottom 0.5,1 -> top 0.5,0)
              ▼
           ◇ d4 (x=760, y=800) ──(right 1,0.5)──▶ Subsystem 4
              │ (bottom 0.5,1)
              └──────────────────────────────────▶ Subsystem 5
```

Notice why this is so clean:
- Every diamond uses at most 3 of its 4 cardinal tips (`Top` in, `Right` out, `Bottom` out).
- Every horizontal branch aligns cleanly with its target subsystem's `entryY` without diagonal spaghetti!
- If two clients (e.g., Mobile App and Admin Web Portal) each have their own vertical diamond cascade bus, offset their `x` coordinates by `>= 60–80px` (e.g., Bus A at `x=940`, Bus B at `x=840`) so their vertical spines never overlap, and any horizontal crossing cleanly renders a crisp `jumpStyle=arc` bridge!

### Fan-In Cascade Pattern (e.g., 5 Returning Paths → 1 Target Action)

```text
Path 1 ──(left)──▶ ◇ m1 ◀──(right)── Path 2
                     │ (top Path 3 optional)
                     ▼ (bottom -> top)
Path 4 ──(left)──▶ ◇ m2 ◀──(right)── Path 5
                     │ (bottom -> top)
                     ▼
              [ Target Action ]
```

---

## 4. Zero Overlapping Lines & Dedicated Corridors

1. **Mandatory Arc Jumps on EVERY Edge**:
   Always include `jumpStyle=arc;jumpSize=8;` on **every** edge — including straight segments, cascade links, cross-lane arrows, and dashed note links. Even if a line doesn't cross anything today, Draw.io only draws an arc at a crossing when the crossing line declares `jumpStyle=arc`.
2. **No Collinear Overlaps (Distinct Corridor Tracks)**:
   When two or more edges travel vertically (e.g., two loop-back arrows or two cancel bypasses going down the left side of a column) or horizontally in the same zone:
   - Assign each edge its own dedicated `x` (for vertical runs) or `y` (for horizontal runs), separated by **at least `40px`**!
   - Example:
     - Inner loop-back (`more → each`): waypoints `(510, 2100) → (510, 1570)`
     - Outer bypass (`hasorders → show`): waypoints `(470, 1440) → (470, 2230)`
     - Separated by `40px` (`470` vs `510`) → zero overlap, crisp visual hierarchy!
3. **Never Route Through Shapes**:
   Calculate exact global bounding boxes (`lane.x + node.x`, `lane.y + node.y`) for every node along an edge's path. If a direct orthogonal line would pass through another node, add explicit `<Array as="points">` waypoints routing around the clear gutter.
4. **Cross-Lane Transitions**:
   When transitioning from Lane A to Lane B:
   - Exit Lane A's node on the side facing Lane B (`Right` if going right, `Left` if going left) or `Bottom` (`0.5, 1` or `0.25, 1`) if dropping down first.
   - Enter Lane B's node on a clear port (`Top 0.25/0.5/0.75` or facing side `Left/Right 0.5`).
   - Place explicit waypoints if any intermediate box sits between the two coordinates.

---

## 5. Edge Label Placement Rules

- **Activity Guards**: Always wrap in `[square brackets]`, e.g., `[cache available]`, `[request fails]`, `[no more items]`.
- **Width & Wrapping**: Set `whiteSpace=wrap;labelBackgroundColor=#ffffff;labelBorderColor=none;spacing=4;labelWidth=<N>;` where `N` is `160–280` depending on guard length.
- **Position Offset (`mxGeometry relative="1" x="<val>"`)**:
  - `x` ranges from `-1.0` (source end) to `+1.0` (target end), with `0` at midpoint.
  - On decision branches, bias the label closer to the decision diamond (e.g., `x="-0.4"` to `-0.7` for long branches) so the reader immediately sees which branch carries which guard, and the label sits on a clear straight span away from corners and neighboring boxes!
- **System Overview Labels**: Use numbered labels (`0.1 Launch App`, `1.1 User Session`, `2.1 Read Catalog`) either directly on the edge (`labelBackgroundColor=#ffffff`) when the span is clear, or as a clean borderless `text` box positioned over a clear horizontal span with zero arrow collision. Prefer direct edge `value` with `labelBackgroundColor=#ffffff` whenever the horizontal span is straight and uncluttered.
