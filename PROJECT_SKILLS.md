# Tire Pros — Project Skill Register

Reviewed October 30, 2026. This register maps available skills to project roles; it does not run agents or change application behavior.

## Newly installed

Installed using the official skill-installer helper from `openai/skills`, `skills/.curated`, default `main` branch. Verified that each destination contains SKILL.md and supporting files. Installation is not an end-to-end runtime test.

| Skill | Primary users | Purpose and stage |
|---|---|---|
| playwright | UI, QA | Real-browser interaction, screenshots, and UI-flow debugging throughout development; especially dashboard, upload, action review, and search acceptance |
| screenshot | UI, QA, release | Windows visual capture when browser-specific screenshots are insufficient; inspect layout and shop-host behavior |
| security-best-practices | Backend, UI, QA | Focused security guidance/reviews when explicitly assigned; includes Python FastAPI, React, and general browser guidance |
| security-threat-model | Manager, backend, QA | Explicitly assigned assessment of upload, customer-data, staff-account, and deployment risks, grounded in the actual implementation |

Install locations: `C:/Users/ndcav/.codex/skills/<skill-name>/`.

These skills will be available on the next user turn. Read their current SKILL.md before applying them and honor each skill's trigger conditions. Installing security skills does not request a full security review now.

Browser automation may require Node/npm, a browser, and an appropriate shell for its CLI wrapper. Verify prerequisites at use time; do not assume installation of a skill installed its runtime dependencies. Use existing project browser tooling when it is sufficient. Windows screenshot helpers are included. No sandbox settings were changed.

## Already available — do not duplicate

| Capability | Available skills | Assignment |
|---|---|---|
| Requirements and scope | superpowers:brainstorming | Manager: clarify material decisions and draft screens without expanding scope |
| Detailed task plans | superpowers:writing-plans | Manager: turn the accepted stage into bounded implementation tasks |
| Delegation | superpowers:dispatching-parallel-agents; superpowers:subagent-driven-development | Manager: independent assignments with clear interfaces and file ownership |
| Sequential execution | superpowers:executing-plans | Manager/implementer: execute authorized tasks and track results |
| Diagnosis and regression checks | superpowers:systematic-debugging; superpowers:test-driven-development | UI/backend: reproduce failures and test meaningful behavior |
| Review | superpowers:requesting-code-review; superpowers:receiving-code-review | Manager/QA: check requirements, review findings, and verify proposed fixes |
| Completion evidence | superpowers:verification-before-completion | All agents: base completion claims on checks actually run |
| Isolation and integration | superpowers:using-git-worktrees; superpowers:finishing-a-development-branch | Manager: isolate conflicting changes when needed and integrate reviewed work |
| PDF inspection | pdf:pdf | Backend/QA: inspect invoice text/layout and verify extraction against original PDFs; this project does not support OCR |
| Historical spreadsheet inspection | spreadsheets:Spreadsheets | Data specialist: inspect and reconcile imports if legacy records arrive as spreadsheet/CSV files |
| Visual concepts | imagegen | UI: static design exploration; mockups do not substitute for working-browser checks |
| OpenAI/Codex guidance | openai-docs | Manager: check official guidance for agent capabilities and configuration |
| Skill maintenance | skill-installer; skill-creator; superpowers:writing-skills | Manager: install or develop additional skills only when a concrete gap emerges |

## Project-specific knowledge

MASTER_PLAN.md and PROJECT_MANAGEMENT.md supply the tire-storage domain rules and operating structure. Read them before assignments. General-purpose skills do not replace the exact $99.99 rate, six-calendar-month period, check-in-date requirement, VIN/set identity, transactional swaps, permanent history, or staged acceptance requirements.

No separate FastAPI/PostgreSQL or tire-domain skill was found in the official curated catalog inspected for this task. Use the existing code, authoritative framework documentation when needed, the master plan, and the installed FastAPI security references. Do not describe a generic skill as specialist domain expertise.

## Selection decisions

- Do not install duplicate PDF, planning, or review skills already supplied by active plugins.
- Do not install cloud hosting skills: the target remains the shop LAN.
- Do not install interactive Playwright for this setup: its inspected instructions currently require disabling sandboxing.
- Do not require Linear, Notion, Figma, GitHub, or another external account just to manage this project. Current Markdown tracking works locally. Revisit integrations if the user chooses those services.
- Security ownership analysis and CI/comment handling can be reconsidered when repository history, GitHub hosting, or CI creates a concrete need.
- Prefer a small applicable toolkit over loading every skill into every specialist's context.

## Manager's assignment rule

Every frontend handoff must require HeroUI for library-covered controls and a source/dependency audit after major adjustments. The reviewer checks actual imports and rendered components, flags newly introduced custom/native replacements, and lists legacy migration debt. Report compliance separately from functional tests; package presence alone is insufficient. Follow MASTER_PLAN.md for exception handling.

Current baseline: existing standard widgets migrated to HeroUI3.2.7. Run `npm run audit:ui` in frontend (also runs automatically during `npm run build`). The AST guard scans production JS/JSX/TS/TSX and import provenance; it supplements, rather than replaces, manual review of domain components and CSS or runtime interaction tests. No approved native-widget exception was needed: PDF selection uses actual HeroUI Input type=file.

Each handoff names the relevant skill(s), project source documents, allowed edits, acceptance criteria, and evidence expected. Delegate only authorized work; parallelize independent tasks, preserve stage gates, and record unresolved prerequisites rather than claiming readiness.

Source catalog: https://github.com/openai/skills/tree/main/skills/.curated
