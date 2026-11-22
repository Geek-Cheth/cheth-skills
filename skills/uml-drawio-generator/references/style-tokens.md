# Draw.io Style Tokens & Geometry Specification

Exact XML attributes, styles, and dimensions derived from the reference UML format. Copy these tokens verbatim to guarantee consistent visual fidelity across all tabs and models.

## 1. File & Page Envelope

```xml
<mxfile host="app.diagrams.net" pages="1">
  <diagram id="unique-tab-id" name="Tab Display Name">
    <mxGraphModel grid="1" page="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" pageScale="1" pageWidth="2400" pageHeight="2800" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- diagram elements -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- Always output **uncompressed** `<mxGraphModel>` inside `<diagram>`.
- `grid="1" gridSize="10"`: All coordinates (`x`, `y`, `width`, `height`, waypoint `x`/`y`) MUST be multiples of `10` (prefer multiples of `20`).
- `pageWidth >= frame.x + frame.width + 60`; `pageHeight >= frame.y + frame.height + 60`.

---

## 2. Outer UML Frame (Required on Every Tab)

### Activity & State Machine Tabs (`container=0`)
Swimlanes, notes, and edges are siblings under `parent="1"` (so edge waypoints use global canvas coordinates).

```xml
<mxCell id="frame" parent="1"
  style="shape=umlFrame;whiteSpace=wrap;width=700;height=35;container=0;collapsible=0;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;"
  value="Diagram Title" vertex="1">
  <mxGeometry x="20" y="20" width="2270" height="2610" as="geometry" />
</mxCell>
```

- Title tab `width`: adjust between `320` and `700` to fit the title cleanly on one line; `height=35`.
- Keep at least `30px` margin on the right and bottom past the furthest lane, note, or waypoint.

### System Overview & Subsystems Tab (`container=1` or `container=0`)
Either `container=0` (all elements under `parent="1"`, simplest for global waypoints) or `container=1` (all overview elements under `parent="frame_1"` with coordinates relative to `frame_1`). Prefer `container=0` with `parent="1"` for simpler absolute coordinate math, or keep every node and edge strictly inside `parent="frame_1"` if using `container=1`. Never mix parent coordinate spaces for waypoints.

```xml
<mxCell id="frame" parent="1"
  style="shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;recursiveResize=0;container=0;collapsible=0;width=640;height=40;fontFamily=Helvetica;fontSize=14;fontStyle=1;strokeColor=#000000;fillColor=#ffffff;fontColor=#000000;"
  value="System Name — System Overview &amp; Subsystems" vertex="1">
  <mxGeometry x="20" y="20" width="2600" height="1680" as="geometry" />
</mxCell>
```

---

## 3. Role Swimlanes (Activity Diagrams)

Each role (e.g., `User`, `Admin`, `Reviewer`, `System`, `Worker`, `External Gateway`) is a vertical swimlane column under `parent="1"`:

```xml
<mxCell id="lane_user" parent="1"
  style="swimlane;horizontal=1;startSize=30;collapsible=0;rounded=0;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;"
  value="User" vertex="1">
  <mxGeometry x="40" y="80" width="400" height="2520" as="geometry" />
</mxCell>
```

- **Multi-role adjacency**: Place roles strictly flush side-by-side (`lane[i].x = lane[i-1].x + lane[i-1].width`), all starting at `y="80"` with identical `height`.
- **Left-gutter notes**: If any note sits on the left of the lanes (`note.x = 40`, `width = 320`), start the first lane at `x = 420` (`60px` gap). Otherwise start the first lane at `x = 40`.
- **Lane width guidelines**:
  - 1 column of actions: `360`–`480`
  - 2 parallel columns: `640`–`960`
  - 3 parallel columns: `1280`–`1480`
- **Children inside a lane**: Every start node, action box, diamond, and end node belonging to a role MUST have `parent="<lane_id>"`, with `x` and `y` **relative to that swimlane's top-left** (`y >= 60`, below the `startSize=30` header).

---

## 4. Core UML Activity & State Nodes

### Initial (Start) Node — `40x40`
```xml
<mxCell id="start" parent="lane_user"
  style="ellipse;aspect=fixed;fillColor=#000000;strokeColor=#000000;fontFamily=Helvetica;fontSize=14;"
  value="" vertex="1">
  <mxGeometry x="180" y="80" width="40" height="40" as="geometry" />
</mxCell>
```

### Final / Flow-Final (End) Node — `40x40`
Used for both main completion and early-exit/error terminations:

```xml
<mxCell id="end_done" parent="lane_system"
  style="shape=sumEllipse;perimeter=ellipsePerimeter;html=1;backgroundOutline=1;aspect=fixed;fillColor=#ffffff;strokeColor=#000000;fontFamily=Helvetica;fontSize=14;"
  value="" vertex="1">
  <mxGeometry x="740" y="2420" width="40" height="40" as="geometry" />
</mxCell>
```

### Action / State Rounded Rectangle
```xml
<mxCell id="act_fetch" parent="lane_system"
  style="rounded=1;arcSize=30;whiteSpace=wrap;align=center;verticalAlign=middle;spacing=8;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;"
  value="Fetch latest records from&#10;primary database" vertex="1">
  <mxGeometry x="580" y="860" width="360" height="80" as="geometry" />
</mxCell>
```

- Standard widths: `240` (states / short actions), `280` (narrow role lane), `320` (default standard), `360` (detailed system actions).
- Standard heights: `60` (1–2 lines) or `80` (2–3 lines). Use `&#10;` or `<br>` for explicit line breaks so text stays cleanly inside the box.

### Decision / Merge / Router Diamond — STRICT `40x40`
```xml
<mxCell id="dec_valid" parent="lane_system"
  style="rhombus;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;"
  value="" vertex="1">
  <mxGeometry x="740" y="480" width="40" height="40" as="geometry" />
</mxCell>
```

- **ALWAYS `width="40" height="40"`** — never oversized (`80x80`, `100x60`) and never filled with condition text in Activity Diagrams.
- Center a diamond horizontally beneath a box: `diamond.x = box.x + (box.width - 40) / 2`.

### UML Note (`shape=note2`)
Placed in the right gutter (`x = last_lane_right + 60`) or left gutter (`x = 40`) under `parent="1"`:

```xml
<mxCell id="note_0" parent="1"
  style="shape=note2;boundedLbl=1;whiteSpace=wrap;size=25;align=left;verticalAlign=top;spacing=14;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;"
  value="Key business invariant or&#10;implementation constraint&#10;explained concisely." vertex="1">
  <mxGeometry x="1940" y="930" width="320" height="140" as="geometry" />
</mxCell>
```

- Standard width: `320`. Height: `100`, `140`, `160`, or `180` depending on line count (`~20px` per line + `40px` padding).

---

## 5. System Overview & Subsystems Nodes (No Images)

### Client / Actor Entry Block (Vector Only — No Screenshots/Images)
```xml
<mxCell id="client_web" parent="1"
  style="rounded=1;arcSize=12;whiteSpace=wrap;align=center;verticalAlign=middle;spacing=12;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;strokeWidth=1.5;"
  value="&lt;b&gt;Admin Web Portal&lt;/b&gt;&lt;br&gt;&lt;br&gt;Roles: Operations Admin, Auditor" vertex="1">
  <mxGeometry x="160" y="540" width="320" height="120" as="geometry" />
</mxCell>
```

### Subsystem Block (`shape=mxgraph.uml25.behaviorAction`)
Standard subsystem (white fill, black stroke):

```xml
<mxCell id="sub_2" parent="1"
  style="shape=mxgraph.uml25.behaviorAction;html=1;rounded=1;absoluteArcSize=1;arcSize=10;align=left;spacingLeft=10;spacingRight=10;whiteSpace=wrap;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;fillColor=#ffffff;"
  value="&lt;b&gt;2. Catalog &amp;amp; Scheduling Subsystem&lt;/b&gt;&lt;br&gt;&lt;br&gt;• Manage item catalog &amp;amp; active schedules&lt;br&gt;• Apply holiday/calendar overrides&lt;br&gt;• Expose availability &amp;amp; open windows" vertex="1">
  <mxGeometry x="1080" y="290" width="440" height="150" as="geometry" />
</mxCell>
```

Highlighted critical / Auth / Entry subsystem (optional soft red accent):
Replace `fillColor=#ffffff;strokeColor=#000000;` with `fillColor=#fad9d5;strokeColor=#ae4132;`.

### External Infrastructure Backdrop Container (Optional)
Render BEFORE the external service blocks so it sits behind them in Z-order:

```xml
<mxCell id="infra_zone" parent="1"
  style="html=1;align=right;verticalAlign=top;rounded=1;absoluteArcSize=1;arcSize=30;dashed=0;spacingTop=12;spacingRight=24;whiteSpace=wrap;fontFamily=Helvetica;fontSize=14;fontStyle=1;fontColor=#ae4132;fillColor=#fad9d5;strokeColor=#ae4132;"
  value="External Services &amp; Data Layer" vertex="1">
  <mxGeometry x="1820" y="80" width="600" height="1520" as="geometry" />
</mxCell>
```

---

## 6. Connectors / Edges (ALL Require `jumpStyle=arc`)

Place ALL edges under `parent="1"` (in `container=0` diagrams) so `<mxPoint>` waypoints are always in global coordinates.

### A. Activity Control Flow & State Transition Edge (Open UML Arrow)
Unlabeled flow:
```xml
<mxCell id="e_01" edge="1" parent="1" source="act_a" target="act_b"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=24;endArrow=open;endFill=0;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;labelBackgroundColor=#ffffff;labelBorderColor=none;whiteSpace=wrap;curved=0;orthogonal=1;jumpStyle=arc;jumpSize=8;exitX=0.5;exitY=1;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;entryPerimeter=0;"
  value="">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

Guarded decision edge (add `labelWidth=<px>;spacing=4;` and `x="<offset>"` on `<mxGeometry>` to position the label cleanly near the decision diamond):
```xml
<mxCell id="e_02" edge="1" parent="1" source="dec_valid" target="act_error"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=24;endArrow=open;endFill=0;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;labelBackgroundColor=#ffffff;labelBorderColor=none;whiteSpace=wrap;labelWidth=180;spacing=4;curved=0;orthogonal=1;jumpStyle=arc;jumpSize=8;exitX=1;exitY=0.5;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;entryPerimeter=0;"
  value="[validation fails]">
  <mxGeometry relative="1" x="-0.4" as="geometry" />
</mxCell>
```

### B. System Overview Flow Edge (Classic Filled Arrow, Numbered Label)
```xml
<mxCell id="sys_e1" edge="1" parent="1" source="sub_1" target="ext_auth"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=24;endArrow=classic;endFill=1;html=1;fontFamily=Helvetica;fontSize=13;fontColor=#000000;strokeColor=#000000;labelBackgroundColor=#ffffff;labelBorderColor=none;whiteSpace=wrap;labelWidth=220;spacing=4;curved=0;orthogonal=1;jumpStyle=arc;jumpSize=8;exitX=1;exitY=0.5;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;entryPerimeter=0;"
  value="1.3 Verify Token &amp; Roles">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### C. UML Note Dashed Link (Arrowless)
```xml
<mxCell id="edge_note_0" edge="1" parent="1" source="act_fetch" target="note_0"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=24;startArrow=none;endArrow=none;endFill=0;dashed=1;html=1;fontFamily=Helvetica;fontSize=14;fontColor=#000000;strokeColor=#000000;labelBackgroundColor=#ffffff;labelBorderColor=none;whiteSpace=wrap;curved=0;orthogonal=1;jumpStyle=arc;jumpSize=8;exitX=1;exitY=0.5;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;entryPerimeter=0;"
  value="">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```
