# canvodpy-extensions: instructions for coding agents

Optional packages for [canvodpy](https://github.com/TUW-GEO/canvodpy).
canvodpy computes vegetation optical depth (VOD) from GNSS signals: a
receiver below a canopy and a reference receiver with open sky
(GNSS-Transmissometry, GNSS-T). Code that serves specific workflows or
data lives here, not in canvodpy. Its users are scientists. The packages
are GitHub-only, never on PyPI.

`CLAUDE.md` files only import this file; edit `AGENTS.md`. Every package
has its own `AGENTS.md`: read it before changing that package.

## Scientific context

canvodpy's root `AGENTS.md` (`canvodpy:AGENTS.md`, "Scientific context")
explains GNSS-T, VOD and the words the code uses (SNR, signal ID, polar
angle, epoch, hemisphere grid). Read it before changing how an extension
converts data; the words are those of canvodpy's glossary
(`canvodpy:GLOSSARY.md`).

## Packages

| Package | Import | Role | Read first |
|---|---|---|---|
| canvod-filemap | `canvod.filemap` | Naming recipes: translate a receiver's own file names to canVOD file names | `packages/canvod-filemap/AGENTS.md` |
| canvod-airflow | `canvod.airflow` | Airflow DAGs that run canvodpy per site and day | `packages/canvod-airflow/AGENTS.md` |
| canvod-adapters | `canvod.adapters` | Data exchange between canvodpy and other GNSS-T programs (gnssvod) | `packages/canvod-adapters/AGENTS.md` |

Each package has its own `pyproject.toml`, version, changelog, tests and
docs page (`docs/packages/<short name>/overview.md`). All packages share
one `.venv` at the root (uv workspace). `canvod` is a namespace package
shared with canvodpy: the `canvod` folder under each `src` has no init
module.

## Task guides

Step-by-step guides for recurring tasks. Claude Code loads them as skills;
other agents read the files directly.

| Task | Guide |
|---|---|
| Release a package, or several | `.claude/skills/release-package/SKILL.md` |
| Change what the extensions need from canvodpy (sources, bounds, relock) | `.claude/skills/canvodpy-dependency/SKILL.md` |
| Write or debug a naming recipe for a receiver | `.claude/skills/naming-recipe/SKILL.md` |
| Support another GNSS-T program in canvod-adapters | `.claude/skills/add-adapter/SKILL.md` |
| Add a new extension package | `.claude/skills/add-package/SKILL.md` |
| Deprecate code | canvodpy's guide, `canvodpy:.claude/skills/deprecate/SKILL.md` |

## Development workflow

Work on a branch, never on `main`; every change reaches `main` through a
pull request. An agent may push its branch and open the pull request, but
never merges, never pushes `main` or tags, never force-pushes and never
bypasses a check (`CODING_STANDARDS.md`, Git and GitHub; enforced for
Claude Code by `scripts/agent_git_guard.py`). Read `CODING_STANDARDS.md`
before writing code: its rules and its checklist apply to every change,
and `/mattpocock-skills:code-review` checks against them. Read the
`AGENTS.md` of every package you change, the task guide if one fits, and
the canvodpy side of the change (below).

Changes go through the agent workflow canvodpy uses (the
mattpocock-skills plugin, `just agent-skills`;
`canvodpy:docs/guides/ai-development.md`). Claude Code calls plugin
skills only by their full name:

| Situation | Start with |
|---|---|
| An idea or a change to design | `/mattpocock-skills:grill-with-docs`: interview until every decision is settled; records terms and decisions (`docs/agents/domain.md` says where) |
| A change too big for one session | `/mattpocock-skills:to-spec`, then `/mattpocock-skills:to-tickets` (GitHub issues), then `/mattpocock-skills:implement` per ticket |
| A change that fits one session | `/mattpocock-skills:implement` (test first with `/mattpocock-skills:tdd`, then `/mattpocock-skills:code-review`) |
| Something is broken | `/mattpocock-skills:diagnosing-bugs`: a command that shows the bug before any theory |
| Not sure | `/mattpocock-skills:ask-matt` |

Releasing is a separate step after merging: see the `release-package`
guide. Running on real data or writing to a production store needs the
maintainers' go-ahead first.

## Commands

```bash
just sync                             # all packages, one .venv, git hooks
just agent-skills                     # the agent workflow plugin (Claude Code)
just check                            # ruff lint + format, ty, agent docs
just test                             # all tests
just test-package canvod-filemap      # one package
just docs                             # preview the docs site
just versions                         # version of every package
just canvodpy-ref                     # canvodpy code this workspace is locked at
just lock-canvodpy                    # relock at the current tip of the canvodpy branch
```

Pre-commit runs ruff, `uv lock`, whitespace checks and the agent docs
check; commitizen checks the commit message; the pre-push hook runs ty.
CI runs `just check-lock`, `just check-lint-only`,
`just check-format-only`, `just check-types` and the tests on Linux,
macOS and Windows.

## Rules

The rules every change follows (free tools only, explicit over implicit,
canvodpy owns the contracts, one implementation per job, composition over
inheritance, deprecate don't delete, write for scientists) are in
`CODING_STANDARDS.md`. They are canvodpy's rules; the reasons are in
canvodpy's decisions (`canvodpy:docs/adr/index.md`).

## Dependency on canvodpy

The extensions import canvodpy packages (canvod-preflight, canvod-readers,
canvod-store, canvod-utils, canvodpy). Root `[tool.uv.sources]` decides
where they come from: a canvodpy branch while the code the extensions need
is unreleased, PyPI otherwise. Read the `canvodpy-dependency` guide before
touching those sources or relocking.

canvodpy in turn installs canvod-filemap as its workspace dependency group
`filemap` (`uv sync --group filemap` in the canvodpy repo), pinned to a tag
of this repo.

## canvodpy: read it before changing an extension

Every extension plugs into canvodpy: its file discovery, readers,
settings, workflows or stores. An extension is only right if it matches
what canvodpy does, so read the canvodpy side first, every time.

**1. Find the canvodpy code this workspace uses.**

```bash
just canvodpy-ref
```

It lists every canvodpy package with its locked version and the source
tree: a commit of a canvodpy branch, or a release tag for packages from
PyPI. They can differ per package. Read canvodpy there, not on its `main`
and not in whatever branch a local checkout is on: with a checkout,
`git -C <canvodpy checkout> show <ref>:<path>`; without one, the GitHub
link printed by the recipe. If the extension needs canvodpy code newer
than that, see the `canvodpy-dependency` guide.

**2. Follow canvodpy's own trail.** canvodpy's agent instructions are its
`AGENTS.md` files:

- `canvodpy:AGENTS.md`, the root. Read at least "Scientific context",
  "Project architecture", "Guardrails" and "Key documentation" (its
  breadcrumb trail, canvodpy's docs in reading order).
- The `AGENTS.md` of each canvodpy package the extension imports, e.g.
  `canvodpy:packages/canvod-readers/AGENTS.md`,
  `canvodpy:packages/canvod-store/AGENTS.md`,
  `canvodpy:packages/canvod-config/AGENTS.md`, `canvodpy:canvodpy/AGENTS.md`.
- `canvodpy:docs/guides/extensions.md`: how canvodpy installs and uses the
  extensions, and what happens when one is missing.

**3. Read what your extension touches** (paths in the canvodpy
repository; docs also at <https://canvodpy.eu/>):

| Extension | canvodpy docs | canvodpy code it must match |
|---|---|---|
| canvod-filemap | `canvodpy:docs/packages/naming/overview.md` (convention, which files a run processes, recipes), `canvodpy:docs/guides/configuration.md` (the `recipe:` setting) | `canvodpy:canvodpy/src/canvodpy/orchestrator/discovery.py` (calls the recipe), `canvodpy:packages/canvod-preflight/src/canvod/preflight/convention.py` |
| canvod-airflow | `canvodpy:docs/guides/api-levels.md`, `canvodpy:docs/guides/parallel-processing.md`, `canvodpy:docs/packages/store/icechunk.md` (concurrent writes) | `canvodpy:canvodpy/src/canvodpy/workflows/tasks.py` (every task the DAGs call) |
| canvod-adapters | `canvodpy:docs/packages/readers/overview.md`, `canvodpy:docs/packages/readers/building-a-reader.md` (reader contract), `canvodpy:docs/packages/vod/overview.md`, `canvodpy:docs/packages/store/overview.md` | `canvodpy:packages/canvod-readers/src/canvod/readers/base.py` (contracts, `GNSSDataReader`) |

**4. Check canvodpy's side of a change.** canvodpy imports canvod-filemap
(`canvodpy.orchestrator.discovery`, its `Justfile`, tests). Before renaming
or changing anything public in an extension, search the canvodpy repository
for it (`git -C <canvodpy checkout> grep -n <name>`) and plan the canvodpy
change too.

### canvodpy facts used throughout

The code is the truth; don't copy these constants into new code.

- canVOD file name (canvod-preflight, `canvod.preflight.convention`):
  `{SIT}{T}{NN}{AGC}_R_{YYYY}{DOY}{HHMM}_{PERIOD}_{SAMPLING}_{CONTENT}.{TYPE}`,
  e.g. `ROSA01TUW_R_20250010000_15M_05S_AA.rnx`. canvodpy finds files by
  this name, or through a naming recipe.
- Observation datasets: dims `(epoch, sid)`, sid `"{sv}|{band}|{code}"`
  (e.g. `G01|L1|C`); checked by `canvod.readers.validate_dataset`. VOD
  datasets: `VOD`, `theta`, `phi` (radians) on `(epoch, sid)`; checked by
  `canvod.readers.validate_vod_dataset`.
- Processing: `canvodpy run --site ... --start ... --end ...`, one day at a
  time, results in Icechunk stores. A store must exist, with its
  repository metadata, before data is written to it.

## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues of TUW-GEO/canvodpy-extensions
(`gh`). See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels (`needs-triage`, `needs-info`,
`ready-for-agent`, `ready-for-human`, `wontfix`). See
`docs/agents/triage-labels.md`.

### Domain docs

canvodpy's glossary and decisions, plus this repository's own decisions.
See `docs/agents/domain.md`.

## Keeping these files useful

- Write what an agent cannot see quickly in the code: decisions, invariants,
  traps, where things live. Don't list functions or restate docstrings;
  point at the file that holds the truth.
- Name the `just` recipe whenever one does the job, not the raw command
  behind it. If no recipe fits a recurring task, add one rather than
  documenting a command.
- Every path and `just` recipe named in `AGENTS.md` and the guides must
  exist: `just check-agent-docs` verifies this (pre-commit and CI).
- Write paths in the canvodpy repository as `canvodpy:<path>`; they are
  checked at the locked canvodpy commit when a canvodpy checkout is next to
  this repository (or at `$CANVODPY_REPO`), and always in CI.
- When a change makes a statement here wrong, fix it in the same PR.
