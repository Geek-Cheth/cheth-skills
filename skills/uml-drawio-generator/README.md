# UML Draw.io Generator Skill

A portable, cross-agent skill for generating standardized, publication-grade UML diagrams in **Draw.io (`.drawio` / uncompressed `mxfile` XML)** format from any system specification, codebase, or workflow description.

## What It Generates

- **System Overview & Subsystems Diagrams**: Left-to-right layered architecture with outer UML frames, vector client blocks (zero embedded images), cascading `40x40` diamond routing buses, UML 2.5 `behaviorAction` subsystem blocks, and external service/database layers.
- **Multi-Role Swimlane UML Activity Diagrams**: Vertical role lanes (`User`, `Admin`, `System`, `Worker`, etc. — 2 to N roles) inside an outer UML frame, `40x40` empty decision/merge diamonds, `[bracketed]` edge guards, and side-gutter UML notes.
- **UML State Machine Diagrams**: Entity lifecycles with `trigger [guard] / effect` transitions, clean self-loops, terminal states, and side-gutter notes.

## Enforced Quality Guarantees

- Outer `shape=umlFrame` on every diagram tab
- Standard `40x40` size on every decision/merge/routing diamond
- Strict **unique port separation** — never joins multiple lines at the same anchor point
- **Cascading separate diamonds** whenever fan-out or fan-in exceeds 3 paths
- Mandatory `jumpStyle=arc;jumpSize=8;` on every connector so crossings are unambiguous
- Dedicated separated corridors (no collinear overlapping lines)
- **Zero embedded images** (pure vector XML)
- Automated verification via `scripts/validate_drawio.py`

## Directory Layout

```text
uml-skill/
├── SKILL.md                               # Main skill entrypoint (Agent Skills standard)
├── README.md                              # Usage & installation guide
├── references/
│   ├── style-tokens.md                    # Exact Draw.io XML styles & dimensions
│   ├── routing-and-diamonds.md            # Diamond cascades, port allocation & corridor rules
│   └── subsystem-and-state-patterns.md    # System Overview & State Machine specifications
├── templates/
│   ├── activity-swimlane-template.drawio  # Validated 3-role Activity Diagram starter
│   ├── subsystem-overview-template.drawio # Validated System Overview starter (no images)
│   └── state-machine-template.drawio      # Validated State Machine starter
└── scripts/
    └── validate_drawio.py                 # Automated zero-dependency XML/layout validator
```

## Using With Any Agent or Model

- **Antigravity / Gemini / Cursor / OpenCode / Codex**: Copy or symlink this folder into `.agents/skills/uml-drawio-generator/` (project-level) or your global skills directory.
- **Claude Code**: Copy or symlink this folder into `.claude/skills/uml-drawio-generator/` or `~/.claude/skills/uml-drawio-generator/`.
- **Any Chat Model**: Reference `SKILL.md` (and the files in `references/`) alongside your system description or codebase and ask it to generate a `.drawio` file.

### Example Prompt

> Using the `uml-drawio-generator` skill, analyze our checkout and payment system in `src/` and generate `architecture.drawio` with:
> 1. A System Overview & Subsystems tab,
> 2. Swimlane Activity Diagram tabs for Checkout and Refund Processing (with Customer, Payment Gateway, and System roles), and
> 3. An Order Status State Machine tab.
> Validate the output with `scripts/validate_drawio.py` before finishing.

## Running the Validator Manually

```bash
python scripts/validate_drawio.py path/to/your-diagram.drawio
```

Add `--strict` to also fail on warnings (grid alignment or guard-bracket warnings).
