# canvodpy-extensions coding standards

Every change follows these. They are canvodpy's standards
(`canvodpy:CODING_STANDARDS.md`), applied to the extensions; where the
extensions differ, this file says so. Read them before writing code;
`/mattpocock-skills:code-review` checks each change against them. Rules a
tool can check (ruff, ty, `just check-agent-docs`, commitizen) are not
repeated here: run `just check`.

## Rules

- **Free tools only.** Nothing in this project may need a paid service or
  API key: not for building, testing, docs or agent tooling.
- **Explicit over implicit.** Fail loudly with a message that says what to
  do. No silent fallback, no hidden default: a default in a signature or a
  documented settings model is fine; library code reading the settings file
  behind the caller's back, or `except Exception` falling back to a value,
  is not.
- **canvodpy owns the contracts.** The dataset structure, the canVOD
  file name and the settings are defined in canvodpy (canvod-readers,
  canvod-preflight, canvod-config). Import them and check against them;
  never copy them here.
- **One implementation per job.** Before writing something, find the code
  that already does it, here or in canvodpy, and reuse it. Processing
  belongs in canvodpy: an extension calls it (canvod-airflow calls
  `canvodpy.workflows.tasks`) and has no pipeline logic of its own. Two
  code paths that do the same job drift apart and give different results.
- **Composition over inheritance.** Pass collaborators in; inherit only
  from pydantic models and from ABC interfaces. Interfaces are ABCs, not
  duck typing. Settings are frozen pydantic models.
- **Deprecate, don't delete.** Public code that goes away gets canvodpy's
  deprecation decorator and stays until the package's next major version;
  see canvodpy's `deprecate` guide
  (`canvodpy:.claude/skills/deprecate/SKILL.md`). Delete outright only
  when the maintainers say so.
- **Write for scientists.** Names, messages, CLI help and docs use clear,
  unambiguous words, the words of canvodpy's glossary
  (`canvodpy:GLOSSARY.md`).
- **Science changes are checked.** A change to how an extension converts
  data (time scales, angles, units, signal IDs) needs the science
  understood first and the primary source named (format specification,
  the other program's documentation, paper).

## Git and GitHub

These hold for every contributor's agent, whatever tool it is.

- **Every change reaches `main` through a pull request.** Work on a
  feature branch, never on `main`.
- **An agent may push its feature branch and open a pull request.**
  Nothing else: it never pushes `main` or a tag, never force-pushes,
  never deletes a remote branch or tag. Push with
  `git push --no-follow-tags`: a git config with `push.followTags` sends
  local tags along otherwise.
- **An agent never merges or approves a pull request.** A person reviews
  and merges, and cuts releases (`just release`, pushing the tag).
- **No bypassing.** No `--no-verify` or `git commit -n`, no skipping,
  redirecting or removing the git hooks (`SKIP=`, `core.hooksPath`,
  `pre-commit uninstall`), no rewriting history that is already on
  GitHub, no changes to branch protection, rulesets, repository settings,
  CI or the agent settings to get a change through. If a check blocks a
  change, fix the change or ask the maintainers.

For Claude Code, `.claude/settings.json` enforces this with deny rules and
a hook (`scripts/agent_git_guard.py`) that blocks such commands. On
GitHub, rulesets require a pull request and passing checks on `main` and
protect release tags.

## Every change

1. **Before changing anything public**, search canvodpy for it
   (`git -C <canvodpy checkout> grep -n <name>`): canvodpy imports
   canvod-filemap. Plan canvodpy's change too.
2. **Tests with the code.** A bug fix gets a test that failed before the
   fix. Expected values come from an independent source (a worked example,
   the specification, the other program's output), never recomputed the
   way the code does it. A test that needs a person, a site or a position
   takes the made-up ones in canvodpy's `canvod.utils.testing`, never real
   people or sites. Tests never read the user's own settings: code that
   loads the settings gets the made-up ones (`testing.write_settings`).
   Use `pathlib`, and `re.escape` on paths in a `match=`: Windows paths
   contain `\`.
3. **Docs in the same pull request**: the package `README.md`, its page
   under `docs/packages/` and the `AGENTS.md` files, wherever the change
   makes them wrong. A pull request that changes behavior without docs to
   match is declined. A new decision that is hard to reverse gets an ADR,
   a new term a glossary entry (`docs/agents/domain.md` says where).
4. **Verify**: `just check`, then `just test-package <package>` for every
   package changed (`just test` when several changed). Report failures;
   don't skip tests.
5. **Commit** on a feature branch in conventional form, scope = package
   short name: `feat(filemap): ...`, `fix(adapters): ...`,
   `docs(airflow): ...`. The per-package changelogs are made from them
   (`cliff.toml`); a commit that changes several packages appears in each
   of their changelogs. Mark breaking changes (`feat!:` or a
   `BREAKING CHANGE:` footer). Substantial agent help is credited with a
   `Co-Authored-By:` line. Push the branch and open a pull request; a
   person merges it (Git and GitHub, above).
6. **Real data and real stores**: running on real data or writing to a
   production store needs the maintainers' go-ahead first; see canvodpy's
   `store-safety` guide (`canvodpy:.claude/skills/store-safety/SKILL.md`).
