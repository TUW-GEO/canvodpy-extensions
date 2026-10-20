"""Naming recipes read from a pinned URL.

A receiver's ``recipe:`` setting can be a raw file link to a recipe in a
GitHub repository, pinned to a commit or a tag::

    https://raw.githubusercontent.com/<account>/<repo>/<commit>/<path>/<name>.yaml
    https://raw.githubusercontent.com/<account>/<repo>/refs/tags/<tag>/<path>/<name>.yaml

A full commit hash is the only pin that never changes: a tag can be moved.
The sha256 of the fetched file, recorded in the store's metadata, says
which recipe a run used.

Fetched recipes are kept in a cache folder in the system's temporary
folder, one per user. The system empties it (macOS removes old files,
Linux clears ``/tmp`` at a restart). A cached recipe is used without a new
fetch, so a run works offline once the recipe was fetched; a recipe whose
tag was moved keeps its old cached copy until the cache is emptied.

A recipe in a private repository needs a GitHub token in the environment
variable ``GH_TOKEN`` or ``GITHUB_TOKEN``. canvodpy stores no secrets
(ADR "Credentials come from the environment" in the canvodpy repository).
The token is only sent to ``raw.githubusercontent.com``, never to the
target of a redirect, and never appears in messages or logs.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import yaml
from pydantic import ValidationError

from .recipe import NamingRecipe
from .recipe_files import recipe_sha256

#: The only host recipes are read from.
RECIPE_HOST = "raw.githubusercontent.com"

#: Environment variables a GitHub token is read from, in this order.
TOKEN_VARIABLES = ("GH_TOKEN", "GITHUB_TOKEN")

#: Largest recipe file accepted, in bytes.
MAX_RECIPE_BYTES = 1_000_000

#: Where downloads go: the recipe URL's path is appended. Tests point it to
#: a local HTTP server.
_DOWNLOAD_ORIGIN = f"https://{RECIPE_HOST}"

_COMMIT = re.compile(r"[0-9a-f]{40}")


class RemoteRecipeError(Exception):
    """A recipe URL that cannot be used."""


class RecipeURLError(RemoteRecipeError, ValueError):
    """A recipe URL that is not a pinned raw file link."""


class RecipeFetchError(RemoteRecipeError):
    """A recipe that could not be fetched, or whose file is not a valid recipe."""


def is_recipe_url(value: str) -> bool:
    """Whether a ``recipe:`` setting is a URL rather than a recipe name.

    Parameters
    ----------
    value : str
        The receiver's ``recipe:`` setting.

    Returns
    -------
    bool
        True for ``https://`` and ``http://`` values.
    """
    return value.lower().startswith(("https://", "http://"))


def check_recipe_url(url: str) -> None:
    """Check that ``url`` is a raw file link pinned to a commit or a tag.

    Parameters
    ----------
    url : str
        The recipe URL.

    Raises
    ------
    RecipeURLError
        If the URL is not ``https``, holds a user name, password, query or
        fragment, points to a host other than ``raw.githubusercontent.com``
        (a ``github.com/.../blob/...`` link gets the matching raw link), is
        pinned to a branch or to a bare name that could be a branch, or
        does not end in a ``.yaml`` or ``.yml`` file.
    """
    parts = urlsplit(url)
    if parts.scheme.lower() != "https":
        msg = f"Recipe URL must start with https://: {url}"
        raise RecipeURLError(msg)
    if parts.username is not None or parts.password is not None:
        msg = (
            "Recipe URL must not hold a user name or password; a token for a "
            f"private repository goes in {' or '.join(TOKEN_VARIABLES)}."
        )
        raise RecipeURLError(msg)
    if parts.query or parts.fragment:
        msg = (
            f"Recipe URL must not have a query ('?') or fragment ('#'): {_shown(url)}. "
            f"A token for a private repository goes in {' or '.join(TOKEN_VARIABLES)}."
        )
        raise RecipeURLError(msg)
    host = (parts.hostname or "").lower()
    segments = [s for s in parts.path.split("/") if s]
    if host == "github.com" and len(segments) > 3 and segments[2] == "blob":
        raw = f"https://{RECIPE_HOST}/" + "/".join(segments[:2] + segments[3:])
        msg = f"Recipe URL is a GitHub page, not the file. Use the raw link: {raw}"
        raise RecipeURLError(msg)
    if host != RECIPE_HOST:
        msg = f"Recipe URL must be a raw file link on {RECIPE_HOST}: {url}"
        raise RecipeURLError(msg)
    if len(segments) < 4:
        msg = f"Recipe URL must be <account>/<repo>/<commit or refs/tags/tag>/<file>: {url}"
        raise RecipeURLError(msg)
    ref = segments[2]
    if _COMMIT.fullmatch(ref):
        file_segments = segments[3:]
    elif ref == "refs" and segments[3] == "tags" and len(segments) > 5:
        file_segments = segments[5:]
    else:
        branch = segments[4] if ref == "refs" and segments[3] == "heads" else ref
        base = f"https://{RECIPE_HOST}/{segments[0]}/{segments[1]}"
        msg = (
            f"Recipe URL must be pinned to a full commit hash or a tag, not '{branch}': "
            f"{url}\nUse {base}/<40-character commit>/... or "
            f"{base}/refs/tags/<tag>/... (a commit is the only pin that never changes)."
        )
        raise RecipeURLError(msg)
    if PurePosixPath(file_segments[-1]).suffix not in (".yaml", ".yml"):
        msg = f"Recipe URL must point to a .yaml or .yml file: {url}"
        raise RecipeURLError(msg)


def recipe_cache_dir() -> Path:
    """The cache folder of fetched recipes, created if missing.

    ``<system temp folder>/canvodpy-recipes-<user id>`` on Linux and macOS,
    readable by its owner only. On Windows the temporary folder already
    belongs to the user, so it is ``<temp folder>/canvodpy-recipes``.

    Returns
    -------
    Path
        The cache folder.

    Raises
    ------
    RecipeFetchError
        On Linux and macOS, if the folder is a link, belongs to another
        user or can be read by others (on a shared ``/tmp``, another user
        could otherwise place a recipe there).
    """
    getuid = getattr(os, "getuid", None)
    if getuid is None:  # Windows: no owner ids; the temp folder is per user
        path = Path(tempfile.gettempdir()) / "canvodpy-recipes"
        path.mkdir(exist_ok=True)
        return path
    path = Path(tempfile.gettempdir()) / f"canvodpy-recipes-{getuid()}"
    path.mkdir(mode=0o700, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != getuid() or info.st_mode & 0o077:
        msg = (
            f"Recipe cache folder {path} is not a folder that only you can "
            "read and write. Remove it; it is created again."
        )
        raise RecipeFetchError(msg)
    return path


def fetch_recipe(url: str, *, timeout: float = 30.0) -> Path:
    """The local file of the recipe at ``url``, fetched if not cached.

    The URL is checked with :func:`check_recipe_url`. A cached copy is used
    if its content still has the sha256 it was stored with. Otherwise the
    file is fetched, read like a local recipe file, and its ``name`` must
    match the file name at the end of the URL; only then is it cached.

    Parameters
    ----------
    url : str
        The recipe URL.
    timeout : float
        Seconds to wait for the server.

    Returns
    -------
    Path
        The cached recipe file.

    Raises
    ------
    RecipeURLError
        If the URL is not a pinned raw file link.
    RecipeFetchError
        If the file cannot be fetched (not found, no access, no network and
        not cached, timeout), is not a valid recipe, its name does not match
        the URL, or the cached copy changed.
    """
    check_recipe_url(url)
    folder = recipe_cache_dir()
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cached = sorted(folder.glob(f"{key}-*.yaml"))
    if len(cached) > 1:
        msg = (
            f"Recipe {url} has more than one cached copy (its tag was moved "
            f"while it was fetched). Remove {folder}; it is created again."
        )
        raise RecipeFetchError(msg)
    if cached:
        path = cached[0]
        if recipe_sha256(path) != path.stem.removeprefix(f"{key}-"):
            msg = f"Cached copy of recipe {url} changed: {path}. Remove it to fetch it again."
            raise RecipeFetchError(msg)
        return path
    data = _download(url, timeout)
    _check_content(url, data)
    path = folder / f"{key}-{hashlib.sha256(data).hexdigest()}.yaml"
    # Written to a new file and renamed: parallel runs may fetch the same URL.
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except OSError as exc:
        Path(tmp).unlink(missing_ok=True)
        # Windows refuses to replace a file another process has open. The
        # name holds the content's sha256, so an existing file is the same
        # recipe, written by a parallel fetch.
        if isinstance(exc, PermissionError) and path.exists():
            return path
        msg = f"Cannot write the cached recipe {path}: {exc}"
        raise RecipeFetchError(msg) from exc
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return path


def _shown(url: str) -> str:
    """``url`` without its query and fragment, for messages."""
    parts = urlsplit(url)
    return parts._replace(query="", fragment="").geturl()


def _token() -> str | None:
    for name in TOKEN_VARIABLES:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def _download(url: str, timeout: float) -> bytes:
    """The bytes of the recipe at ``url``; the token goes only to the first host."""
    request = urllib.request.Request(
        _DOWNLOAD_ORIGIN + urlsplit(url).path,
        headers={"User-Agent": "canvod-filemap"},
    )
    token = _token()
    if token:
        # Not forwarded when the server redirects (urllib copies other headers).
        request.add_unredirected_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(MAX_RECIPE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        msg = f"Recipe {url} could not be fetched: HTTP {exc.code} {exc.reason}."
        if exc.code == 404:
            msg = f"Recipe not found: {url}."
            if token is None:
                msg += (
                    " A recipe in a private repository needs a GitHub token in "
                    f"{' or '.join(TOKEN_VARIABLES)}."
                )
            else:
                msg += " If the repository is private, check that the token can read it."
        elif exc.code in (401, 403) and token is not None:
            msg += " The token was refused, or GitHub limits the requests; try again later."
        elif exc.code in (401, 403, 429):
            msg += " GitHub limits the requests; try again later."
        raise RecipeFetchError(msg) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        msg = (
            f"Recipe {url} could not be fetched ({reason}) and is not in the "
            "cache. A run without network access needs the recipe fetched once before."
        )
        raise RecipeFetchError(msg) from None
    if len(data) > MAX_RECIPE_BYTES:
        msg = f"Recipe {url} is larger than {MAX_RECIPE_BYTES} bytes; it is not a recipe."
        raise RecipeFetchError(msg)
    return data


def _check_content(url: str, data: bytes) -> None:
    """Read ``data`` like a local recipe file and check its name against ``url``."""
    try:
        recipe = NamingRecipe.from_yaml(data.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        msg = f"Recipe {url} is not a YAML file: {exc}"
        raise RecipeFetchError(msg) from None
    except ValidationError as exc:
        msg = f"Recipe {url} is not a valid recipe:\n{exc}"
        raise RecipeFetchError(msg) from None
    stem = PurePosixPath(urlsplit(url).path).stem
    if recipe.name != stem:
        msg = (
            f"Recipe {url} is named '{recipe.name}', but its file is '{stem}'. "
            "The recipe's name must match its file name."
        )
        raise RecipeFetchError(msg)
