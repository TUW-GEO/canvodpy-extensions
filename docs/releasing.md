---
title: How a release works
description: The release chain of the extension packages, from commit message to PyPI upload
---

# How a release works

This page documents the release chain of the extension packages, from
commit message to PyPI upload. The steps to follow are in
[Contributing](CONTRIBUTING.md#releasing). canVODpy's own chain is in
[How the release infrastructure works](https://canvodpy.eu/guides/HOW_RELEASE_WORKS/);
the extensions differ in one point: **each package is released on its
own**, with its own version, tag, GitHub release, and PyPI upload.

---

## 1. Conventional commits

Commit messages follow `type(scope): subject`, for example
`fix(filemap): handle an empty recipe file`. The commit-msg hook
(installed by `just hooks`) runs commitizen's check and rejects other
messages. The messages become the changelog, so mark breaking changes
(`feat!:` or a `BREAKING CHANGE:` footer).

---

## 2. Versions, changelogs, and tags

| Recipe | What it does |
|--------|--------------|
| `just versions` | Prints the version of every package |
| `just changelog canvod-filemap` | Prints the package's changes since its last release |
| `just release canvod-filemap 1.1.0` | Runs the package's tests, sets the version (`major`, `minor`, `patch`, or a version number), writes the package's `CHANGELOG.md`, and makes one release commit |
| `just tag canvod-filemap` | On an up-to-date `main`, tags the package's version and pushes the tag |

**Changelogs.** Every package has a `CHANGELOG.md` in its folder.
[git-cliff](https://git-cliff.org) (`cliff.toml`) writes it from the commits
that changed `packages/<package>/`. Edit the new section in the release
pull request where an entry is wrong or missing: the draft release takes
its notes from it.

**Tags.** A release is the tag `<package>-v<version>`, for example
`canvod-filemap-v1.1.0`. `just release` refuses a version whose tag exists
already. `just tag` refuses to tag unless `main` matches `origin/main` and
the package's `CHANGELOG.md` has a section for the tag, so a tag always
points at a merged release commit.

`main` requires a pull request, so the release commit goes through one:
`just release` on a branch, pull request, merge, then `just tag` on `main`.
Tagging before the merge can leave the tag on a commit that never reaches
`main`.

---

## 3. Draft releases

`.github/workflows/release.yml` runs when a tag `canvod-*-v*` is pushed:

1. Reads the package and version from the tag and stops if the tag names no
   package under `packages/` or doesn't match the package's version.
2. Takes the release notes from the tag's section of the package's
   `CHANGELOG.md`, as edited in the release pull request, and stops if
   there is none.
3. Creates a **draft** release titled `<package> <version>` (a pre-release
   for `a`, `b` and `rc` versions).

A maintainer reviews the draft and publishes it. Publishing archives the
repository on Zenodo, versioned by the tag. `.zenodo.json` and
`CITATION.cff` carry no version, since the packages have different ones.

---

## 4. PyPI publishing

`.github/workflows/publish_pypi.yml` runs only when started by hand, on a
release tag:

```bash
gh workflow run publish_pypi.yml --ref canvod-filemap-v1.1.0
```

Tagging and publishing to PyPI are separate decisions: a tag isn't a
promise that PyPI has the version.

**Build job** (no upload permission):

1. Stops unless it runs on a tag, the tag names a package under
   `packages/`, and the tag matches the package's version.
2. Builds exactly that package with `uv build --no-sources`: as PyPI users
   get it, without the git sources of `[tool.uv.sources]`.
3. Refuses a wheel with a dependency on a URL (`pkg @ git+https://...`),
   which PyPI rejects.

**Publish job:** runs in the GitHub environment `pypi`. The environment
needs a maintainer's approval before the job starts, and accepts only tags
`canvod-*-v*`. The job uploads with `uv publish --trusted-publishing always`.

**Dependencies first.** Every dependency of a package must be on PyPI
before the package can be installed from there. The extensions depend on
canVODpy packages (`canvodpy`, `canvod-utils` and others), so a canVODpy
release that an extension needs goes to PyPI first.

Uploads to PyPI are permanent: a version can't be uploaded twice, so a
broken release is fixed by the next patch version.

---

## 5. Trusted publishing with OIDC

The publish job proves to PyPI which repository, workflow, and environment
it runs in, with a short-lived token from GitHub; no PyPI token is stored
anywhere. The details are in canVODpy's
[OIDC trusted publishing explained](https://canvodpy.eu/guides/OIDC_EXPLAINED/).

Each package is its own project on PyPI and needs the trusted publisher
once:

```
Owner:             TUW-GEO
Repository name:   canvodpy-extensions
Workflow name:     publish_pypi.yml
Environment name:  pypi
```

**New package:** a package that isn't on PyPI yet has no project to add the
publisher to. Add a *pending* publisher instead, under Publishing in your PyPI account
settings. It takes the package name and the four fields of the preceding
block.
The first upload creates the project and turns the pending publisher into a
normal one. PyPI can refuse a second pending publisher while one is pending;
then upload that package first.

---

## Complete example

Releasing a fix in canvod-filemap:

```bash
git switch main && git pull origin main
just changelog canvod-filemap
git switch -c chore/release-canvod-filemap-1.0.1
just release canvod-filemap patch
git push -u origin chore/release-canvod-filemap-1.0.1
gh pr create --fill
# merged once CI passes, then on main:
git switch main && git pull origin main
just tag canvod-filemap
# draft release "canvod-filemap 1.0.1" appears: review, publish
gh workflow run publish_pypi.yml --ref canvod-filemap-v1.0.1
# approve the pypi environment when GitHub asks
```

Users then update with `uv add canvod-filemap==1.0.1`.

---

## Troubleshooting

### Release commit refused

`Tag <tag> exists already`: choose the next version. `Commit or discard
your changes first`: `just release` needs a clean working tree.

### Tag refused

`main differs from origin/main`: `git pull` first. `<tag> is not in
packages/<package>/CHANGELOG.md`: the release commit isn't on `main` yet;
merge its pull request first.

### Draft release missing

The tag must have the form `<package>-v<version>` and match the version in
`packages/<package>/pyproject.toml` on the tagged commit.

### PyPI workflow fails at once

`Run this workflow on a release tag`: start it with
`--ref <package>-v<version>`, not on a branch.

### Upload refused by PyPI

Check that the project on PyPI has the trusted publisher of section 5, with the
same repository, workflow file, and environment name. A package that isn't
on PyPI yet needs a pending publisher.
