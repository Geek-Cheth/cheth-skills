# cheth-skills

Personal multi-agent skills monorepo. One git repo, many skills, synced via junctions into Cursor, Codex, Antigravity, Claude Code, and T3 Code provider instances.

## Skills catalog

| Skill | Path | Description |
| --- | --- | --- |
| `uml-drawio-generator` | [`skills/uml-drawio-generator/`](skills/uml-drawio-generator/) | Generate clean, standardized UML diagrams in Draw.io (`.drawio` / mxfile XML) — activity swimlanes, subsystem overviews, and state machines. |

## Add a new skill

1. Create `skills/<skill-name>/SKILL.md` (plus any `references/`, `scripts/`, `templates/`, etc.).
2. Re-run the sync script so every agent picks it up:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-skills.ps1
```

## Install / sync (Windows)

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-skills.ps1
```

The script is idempotent and needs no admin. It discovers every `skills/*/SKILL.md` and creates (or refreshes) directory junctions:

| Agent / surface | Junction destination |
| --- | --- |
| Cursor (standalone + T3 Code Cursor) | `%USERPROFILE%\.cursor\skills\<skillName>` |
| Codex (standalone + T3 Code Codex shadow) | `%USERPROFILE%\.codex\skills\<skillName>` |
| Universal `.agents` | `%USERPROFILE%\.agents\skills\<skillName>` |
| Claude Code | `%USERPROFILE%\.claude\skills\<skillName>` |
| Antigravity (standalone) | `%USERPROFILE%\.gemini\config\plugins\cheth-skills` (whole repo) |
| Antigravity (T3 Code instances) | `%USERPROFILE%\.t3\userdata\providers\antigravity\*\config\plugins\cheth-skills` |

It never overwrites real folders, and it refuses reserved / protected names such as `.system`, `skills-cursor`, and `builtin`.

## Plugin manifest

Root [`plugin.json`](plugin.json) identifies this repo as the Antigravity plugin `cheth-skills` (author: Chethina).
