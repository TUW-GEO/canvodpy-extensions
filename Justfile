# ============================================================================
# canvodpy-extensions Monorepo - Root Justfile
# ============================================================================

# ANSI color codes
GREEN := '\033[0;32m'
BOLD := '\033[1m'
NORMAL := '\033[0m'

# Default command lists all available recipes
_default:
    @just --list --unsorted

alias c := clean
alias h := hooks
alias q := check
alias t := test

# ============================================================================
# Setup
# ============================================================================

# install dependencies and ensure all git hooks are active
sync:
    uv sync
    uv run pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

# install pre-commit, commit-msg and pre-push git hooks
hooks:
    uv run pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

# install or update the shared agent workflow skills (Claude Code plugin from GitHub mattpocock/skills, the same as canvodpy's)
agent-skills:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v claude >/dev/null 2>&1; then
        echo "Claude Code ('claude') is not installed: https://code.claude.com/docs" >&2
        echo "Other coding agents: npx skills@latest add mattpocock/skills" >&2
        exit 1
    fi
    # the author's own marketplace (GitHub mattpocock/skills): its latest release,
    # which the official Claude marketplace may lag behind
    claude plugin marketplace add mattpocock/skills --scope project
    claude plugin install mattpocock-skills@mattpocock --scope project
    claude plugin marketplace update mattpocock

# ============================================================================
# Code Quality
# ============================================================================

# check uv.lock is up to date (for CI)
check-lock:
    uv lock --check

# show the canvodpy version or commit every canvodpy package is locked at
canvodpy-ref:
    @uv run --no-sync python tools/canvodpy_ref.py

# relock every canvodpy package taken from git at the current tip of its source
lock-canvodpy:
    #!/usr/bin/env bash
    set -euo pipefail
    # uv keeps the locked commit of a git repository while any package from
    # it is not upgraded, so all of them are upgraded together
    pkgs=$(uv run --no-sync python -c 'import tomllib; lock = tomllib.load(open("uv.lock", "rb")); print(" ".join(p["name"] for p in lock["package"] if "TUW-GEO/canvodpy.git" in p.get("source", {}).get("git", "")))')
    test -n "${pkgs}" || { echo "No canvodpy package is taken from git" >&2; exit 0; }
    args=()
    for p in ${pkgs}; do args+=(--upgrade-package "${p}"); done
    uv lock --no-cache "${args[@]}"
    echo "canvodpy commit(s) in uv.lock:"
    grep -o 'TUW-GEO/canvodpy.git[^"]*#[0-9a-f]*' uv.lock | sed 's/.*#//' | sort -u

# lint python code using ruff
[private]
check-lint:
    uv run ruff check . --fix

# lint python code without auto-fixing (for CI)
check-lint-only:
    uv run ruff check .

# format python code using ruff
[private]
check-format:
    uv run ruff format .

# check formatting without modifying files (for CI)
check-format-only:
    uv run ruff format --check .

# run the type checker ty (config lives in [tool.ty] in pyproject.toml)
check-types:
    uv run ty check

# check that AGENTS.md files and skills name only existing paths and recipes
check-agent-docs:
    uv run --no-sync python tools/check_agent_docs.py

# lint, format and type-check all packages, check the agent docs
check: check-lint check-format check-types check-agent-docs

# run all tests
test:
    uv run pytest

# run all tests with coverage report
test-coverage:
    uv run pytest

# run tests for a single package, e.g. `just test-package canvod-filemap`
test-package PKG:
    uv run pytest packages/{{PKG}}/tests

# ============================================================================
# Cleanup
# ============================================================================

# remove build artifacts, caches and bytecode
clean:
    rm -fr dist/ build/ .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '__pycache__' -exec rm -fr {} +
    find . -name '.pytest_cache' -exec rm -fr {} +
    find . -name '.ruff_cache' -exec rm -fr {} +

# ============================================================================
# Documentation
# ============================================================================

# preview the documentation locally
docs:
    uv run zensical serve --open

# build the documentation
docs-build:
    uv run zensical build

# check the language of the docs pages (Vale, Google style)
docs-lint *FILES="docs CONTRIBUTING.md":
    uvx --from vale vale sync
    uvx --from vale vale {{ FILES }}

# check the language of the docs pages and CONTRIBUTING.md changed since
# BASE (Vale; what CI runs)
docs-lint-changed BASE="origin/main":
    #!/usr/bin/env bash
    set -euo pipefail
    files=$(git diff --name-only --diff-filter=d "{{ BASE }}...HEAD" -- 'docs/*.md' 'docs/**/*.md' CONTRIBUTING.md)
    if [ -z "$files" ]; then echo "No docs pages changed since {{ BASE }}."; exit 0; fi
    uvx --from vale vale sync
    uvx --from vale vale $files

# check every link of the built docs site (lychee; brew install lychee)
docs-links:
    @command -v lychee >/dev/null || { echo "lychee is not installed: brew install lychee" >&2; exit 1; }
    uv run zensical build --clean
    lychee --root-dir "$(pwd)/site" 'site/**/*.html'

# deploy the documentation via GitHub Actions
docs-deploy:
    gh workflow run "Deploy Docs"

# ============================================================================
# Release Management
# ============================================================================

# Each package is released on its own, under the tag <package>-v<version>
# (e.g. canvod-filemap-v0.2.0). See "Releasing" in CONTRIBUTING.md.

# show the version of every package
versions:
    @for pkg in packages/*/; do pkg=$(basename "$pkg"); echo "$pkg $(uv version --package "$pkg" --short --frozen)"; done

# show the changes to PKG since its last release
changelog PKG:
    uvx git-cliff --include-path "packages/{{PKG}}/**" --tag-pattern "^{{PKG}}-v[0-9]" --unreleased

# release commit for PKG: bump (major, minor, patch or e.g. 0.2.0), changelog
release PKG VERSION: (test-package PKG)
    #!/usr/bin/env bash
    set -euo pipefail
    test -d "packages/{{PKG}}" || { echo "No package packages/{{PKG}}" >&2; exit 1; }
    test -z "$(git status --porcelain)" || { echo "Commit or discard your changes first" >&2; exit 1; }
    case "{{VERSION}}" in
        major|minor|patch) uv version --package "{{PKG}}" --bump "{{VERSION}}" ;;
        *) uv version --package "{{PKG}}" "{{VERSION}}" ;;
    esac
    version=$(uv version --package "{{PKG}}" --short --frozen)
    tag="{{PKG}}-v${version}"
    if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
        echo "Tag ${tag} exists already" >&2; exit 1
    fi
    uvx git-cliff --include-path "packages/{{PKG}}/**" --tag-pattern "^{{PKG}}-v[0-9]" \
        --tag "${tag}" --output "packages/{{PKG}}/CHANGELOG.md"
    # git-cliff ends the file with a blank line, which end-of-file-fixer
    # would change in the commit below and so stop it
    perl -0pi -e 's/\n+\z/\n/' "packages/{{PKG}}/CHANGELOG.md"
    git add "packages/{{PKG}}" uv.lock
    git commit -m "chore(release): {{PKG}} ${version}"
    echo ""
    echo -e "{{GREEN}}{{BOLD}}Release commit for ${tag} created.{{NORMAL}}"
    echo ""
    echo "Next steps (main requires a PR, see CONTRIBUTING.md):"
    echo "  1. Push this branch, open a PR and merge it"
    echo "  2. git checkout main && git pull, then: just tag {{PKG}}"
    echo "  3. Publish the draft GitHub Release that the tag creates"
    echo "  4. Publish to PyPI: gh workflow run publish_pypi.yml --ref ${tag}"
    echo "  5. Downstream, raise the lower bound if needed (canvodpy's filemap group)"

# tag the current version of PKG on an up-to-date main and push the tag
tag PKG:
    #!/usr/bin/env bash
    set -euo pipefail
    git fetch --quiet origin main --tags
    test "$(git branch --show-current)" = main || { echo "Check out main first" >&2; exit 1; }
    test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" || { echo "main differs from origin/main: git pull first" >&2; exit 1; }
    version=$(uv version --package "{{PKG}}" --short --frozen)
    tag="{{PKG}}-v${version}"
    grep -q "\[${tag}\]" "packages/{{PKG}}/CHANGELOG.md" || { echo "${tag} is not in packages/{{PKG}}/CHANGELOG.md: run just release first" >&2; exit 1; }
    git tag -a "${tag}" -m "{{PKG}} ${version}"
    git push origin "${tag}"
