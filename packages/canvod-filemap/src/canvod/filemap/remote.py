"""Naming recipes read from a pinned URL.

A receiver's ``recipe:`` setting can be a raw file link to a recipe in a
GitHub repository, pinned to a commit or a tag::

    https://raw.githubusercontent.com/<account>/<repo>/<commit>/<path>/<name>.yaml
    https://raw.githubusercontent.com/<account>/<repo>/refs/tags/<tag>/<path>/<name>.yaml

A full commit hash is the only pin that never changes: a tag can be moved.
The sha256 of the fetched file, recorded in the store's metadata, says
which recipe a run used.

Fetched recipes are kept in a cache folder in the system's temporary
folder, one per user. A cached recipe is used without a new fetch, so a
run works offline once the recipe was fetched; a recipe whose tag was
moved keeps its old cached copy until the cache is emptied.

A recipe in a private repository needs a GitHub token in the environment
variable ``GH_TOKEN`` or ``GITHUB_TOKEN``. canvodpy stores no secrets
(ADR "Credentials come from the environment" in the canvodpy repository).
The token is only sent to ``raw.githubusercontent.com``, never to the
target of a redirect, and never appears in messages or logs.

The URL check, token, download and cache are canvodpy's
:mod:`canvod.utils.pinned`, which also reads settings files from a URL;
this module adds the recipe check and keeps the recipe names and errors.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import yaml
from canvod.utils import pinned
from canvod.utils.pinned import PinnedFetchError, PinnedURLError
from pydantic import ValidationError

from .recipe import NamingRecipe

#: The only host recipes are read from.
RECIPE_HOST = pinned.PINNED_HOST

#: Environment variables a GitHub token is read from, in this order.
TOKEN_VARIABLES = pinned.TOKEN_VARIABLES

#: Largest recipe file accepted, in bytes.
MAX_RECIPE_BYTES = 1_000_000


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
    return pinned.is_url(value)


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
    try:
        pinned.parse_pinned_url(url, what="recipe")
    except PinnedURLError as exc:
        raise RecipeURLError(str(exc)) from None


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
    try:
        return pinned.cache_dir("recipes")
    except PinnedFetchError as exc:
        raise RecipeFetchError(str(exc)) from None


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
        If the file cannot be fetched (not found, no access, a token that
        is not a token, no network and not cached, timeout), is not a valid
        recipe, its name does not match the URL, or the cached copy changed.
    """
    try:
        return pinned.fetch_pinned(
            url,
            kind="recipes",
            what="recipe",
            check=lambda data: _check_content(url, data),
            max_bytes=MAX_RECIPE_BYTES,
            timeout=timeout,
        )
    except PinnedURLError as exc:
        raise RecipeURLError(str(exc)) from None
    except PinnedFetchError as exc:
        raise RecipeFetchError(str(exc)) from None


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
