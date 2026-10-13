"""Check that the agent instructions name only paths and recipes that exist.

Reads ``AGENTS.md``, ``packages/*/AGENTS.md``,
``.claude/skills/*/SKILL.md`` and ``CODING_STANDARDS.md``. A path in
backticks must exist relative to the repository root or to the file's
directory; a ``just <recipe>`` must be a recipe of the root Justfile; a
``/<skill>`` must be a skill of ``.claude/skills/``, a
``/mattpocock-skills:<skill>`` a skill of the plugin (Claude Code calls
plugin skills only by their full name). ``canvodpy:<path>`` names a path in the
canvodpy repository; it is checked at the canvodpy commit the workspace is
locked at (``canvodpy_ref.reference``) if a canvodpy git checkout is found
(``$CANVODPY_REPO``, or ``canvodpy`` next to this repository). Placeholders
(``<...>``, ``PKG``, ``*``) and the paths listed below are not checked.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from canvodpy_ref import reference

ROOT = Path(__file__).resolve().parent.parent

#: Paths outside this repository: git refs, temporary files.
OTHER_REPO_PREFIXES = ("origin/", "/tmp/")

#: Prefix of a path in the canvodpy repository.
CANVODPY = "canvodpy:"

#: Files of the user's canvodpy configuration.
USER_FILES = frozenset({"canvod-settings.yaml"})

#: Recipes of the canvodpy Justfile, named in the guides.
OTHER_REPO_RECIPES = frozenset({"naming-init", "config-check-data"})

#: Skills of the mattpocock-skills plugin (``just agent-skills``), version
#: 1.3.1, as in canvodpy's check. The files name them
#: ``/mattpocock-skills:<name>``; update this list when the plugin adds or
#: renames one.
PLUGIN_SKILLS = frozenset({
    "ask-matt", "code-review", "codebase-design", "diagnosing-bugs",
    "domain-modeling", "grill-me", "grill-with-docs", "grilling", "handoff",
    "implement", "implement-spec", "improve-codebase-architecture", "pr",
    "prototype", "research", "retro", "setup-matt-pocock-skills", "tdd",
    "teach", "to-questionnaire", "to-spec", "to-tickets", "triage",
    "wait-what", "wayfinder", "wizard", "writing-for-agents",
})  # fmt: skip
PLUGIN = "mattpocock-skills"

_SKILL = re.compile(r"/(?:(?P<plugin>[a-z][a-z0-9-]*):)?(?P<name>[a-z][a-z0-9-]*)")
_CODE_SPAN = re.compile(r"`([^`\n]+)`")
_FENCE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_JUST = re.compile(r"(?:^|[\s`(])just ([a-z][a-z0-9-]*)")
_PATH_SUFFIXES = (".md", ".py", ".toml", ".yaml", ".yml", ".ini", ".lock")
_PLACEHOLDER = re.compile(r"[<>*{}]|PKG|X\.Y\.Z")


def agent_files() -> list[Path]:
    return [
        ROOT / "AGENTS.md",
        *sorted(ROOT.glob("packages/*/AGENTS.md")),
        *sorted(ROOT.glob(".claude/skills/*/SKILL.md")),
        ROOT / "CODING_STANDARDS.md",
    ]


def own_skills() -> set[str]:
    return {path.parent.name for path in ROOT.glob(".claude/skills/*/SKILL.md")}


def skill_problem(span: str, plugin: str | None, name: str) -> str | None:
    """Return why ``span`` does not call a skill, or None."""
    if plugin is None:
        if name in own_skills():
            return None
        if name in PLUGIN_SKILLS:
            return f"`{span}` is a plugin skill; write `/{PLUGIN}:{name}`"
        return f"`{span}` is not a skill"
    if plugin != PLUGIN or name not in PLUGIN_SKILLS:
        return f"`{span}` is not a skill"
    return None


def canvodpy_repo() -> Path | None:
    repo = Path(os.environ.get("CANVODPY_REPO", ROOT.parent / "canvodpy"))
    return repo if (repo / "canvodpy" / "pyproject.toml").is_file() else None


def just_recipes() -> set[str]:
    out = subprocess.run(
        ["just", "--summary"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return set(out.split())


def is_path(span: str) -> bool:
    if " " in span or span.startswith(("http", "-")) or _PLACEHOLDER.search(span):
        return False
    return "/" in span or span.endswith(_PATH_SUFFIXES)


def git_object_exists(repo: Path, spec: str) -> bool:
    """Whether the git object ``spec`` exists in ``repo``.

    Git sets ``GIT_DIR`` and friends for hooks; they would point this call
    at this repository instead of ``repo``.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    cmd = ["git", "-C", str(repo), "cat-file", "-e", spec]
    return subprocess.run(cmd, env=env, capture_output=True).returncode == 0


def in_canvodpy(repo: Path, ref: str, path: str) -> bool:
    """Whether ``path`` exists in the canvodpy checkout ``repo`` at ``ref``."""
    return git_object_exists(repo, f"{ref}:{path.rstrip('/')}")


def problems(file: Path, recipes: set[str], canvodpy: tuple[Path, str] | None) -> list[str]:
    text = file.read_text(encoding="utf-8")
    found = []
    for span in _CODE_SPAN.findall(_FENCE.sub("", text)):
        if span.startswith(CANVODPY):
            path = span.removeprefix(CANVODPY)
            if canvodpy and not _PLACEHOLDER.search(path) and not in_canvodpy(*canvodpy, path):
                found.append(f"path `{path}` does not exist in canvodpy at {canvodpy[1]}")
            continue
        if skill := _SKILL.fullmatch(span):
            if reason := skill_problem(span, skill["plugin"], skill["name"]):
                found.append(reason)
            continue
        if not is_path(span) or span.startswith(OTHER_REPO_PREFIXES) or span in USER_FILES:
            continue
        if not ((ROOT / span).exists() or (file.parent / span).exists()):
            found.append(f"path `{span}` does not exist")
    for recipe in _JUST.findall(text):
        if recipe not in recipes and recipe not in OTHER_REPO_RECIPES:
            found.append(f"`just {recipe}` is not a recipe")
    return found


def main() -> int:
    recipes = just_recipes()
    repo = canvodpy_repo()
    canvodpy = None
    if repo is None:
        print("No canvodpy checkout found: canvodpy paths not checked")
    else:
        ref = reference()
        if not git_object_exists(repo, f"{ref}^{{commit}}"):
            print(f"canvodpy {ref} is not in {repo}: fetch it (git -C {repo} fetch --tags origin)")
            return 1
        canvodpy = (repo, ref)
    failed = False
    for file in agent_files():
        for problem in problems(file, recipes, canvodpy):
            print(f"{file.relative_to(ROOT)}: {problem}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
