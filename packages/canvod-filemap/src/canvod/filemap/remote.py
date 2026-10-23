"""Naming recipes read from a URL.

A receiver's ``recipe:`` setting can be a raw file link to a recipe in a
GitHub repository, at a commit, a tag or a branch::

    https://raw.githubusercontent.com/<account>/<repo>/<commit>/<path>/<name>.yaml
    https://raw.githubusercontent.com/<account>/<repo>/refs/tags/<tag>/<path>/<name>.yaml
    https://raw.githubusercontent.com/<account>/<repo>/refs/heads/<branch>/<path>/<name>.yaml

The user is responsible for what the link points to. Every run fetches
the recipe again; there is no cache, so a run needs network access. The
sha256 of the fetched file, recorded in the store's metadata with the
file name of the URL (never the URL), says which recipe a run used.

A recipe in a private repository needs a GitHub token in the environment
variable ``GH_TOKEN`` or ``GITHUB_TOKEN``. canvodpy stores no secrets
(ADR "Credentials come from the environment" in the canvodpy repository).
The token is only sent to ``raw.githubusercontent.com``, never to the
target of a redirect, and never appears in messages or logs.

The URL check, token and download are canvodpy's
:mod:`canvod.utils.remote_file`, which also reads settings files from a
URL; this module adds the recipe check and keeps the recipe names and
errors.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import yaml
from canvod.utils import remote_file
from canvod.utils.remote_file import RemoteFetchError, RemoteURLError
from pydantic import ValidationError

from .recipe import NamingRecipe

#: The only host recipes are read from.
RECIPE_HOST = remote_file.REMOTE_HOST

#: Environment variables a GitHub token is read from, in this order.
TOKEN_VARIABLES = remote_file.TOKEN_VARIABLES

#: Largest recipe file accepted, in bytes.
MAX_RECIPE_BYTES = 1_000_000


class RemoteRecipeError(Exception):
    """A recipe URL that cannot be used."""


class RecipeURLError(RemoteRecipeError, ValueError):
    """A recipe URL that is not a raw file link."""


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
    return remote_file.is_url(value)


def check_recipe_url(url: str) -> None:
    """Check that ``url`` is a raw file link in a GitHub repository.

    Parameters
    ----------
    url : str
        The recipe URL.

    Raises
    ------
    RecipeURLError
        If the URL is not ``https``, holds a user name, password, query or
        fragment, points to a host other than ``raw.githubusercontent.com``
        (a ``github.com/.../blob/...`` link gets the matching raw link),
        has no ``<account>/<repo>/<commit, tag or branch>/<file>`` path, or
        does not end in a ``.yaml`` or ``.yml`` file.
    """
    try:
        remote_file.parse_remote_url(url, what="recipe")
    except RemoteURLError as exc:
        raise RecipeURLError(str(exc)) from None


def fetch_recipe(url: str, *, timeout: float = 30.0) -> Path:
    """The local file of the recipe at ``url``, fetched by this run.

    The URL is checked with :func:`check_recipe_url`. The file is fetched,
    read like a local recipe file, and its ``name`` must match the file
    name at the end of the URL. A run fetches a URL once, into a folder
    of the run that is removed when the process that made it ends
    (:func:`canvod.utils.remote_file.fetch_remote`).

    Parameters
    ----------
    url : str
        The recipe URL.
    timeout : float
        Seconds to wait for the server.

    Returns
    -------
    Path
        The fetched recipe file.

    Raises
    ------
    RecipeURLError
        If the URL is not a raw file link.
    RecipeFetchError
        If the file cannot be fetched (not found, no access, a token that
        is not a token, no network, timeout), is not a valid recipe, or its
        name does not match the URL.
    """
    try:
        return remote_file.fetch_remote(
            url,
            what="recipe",
            check=lambda data: _check_content(url, data),
            max_bytes=MAX_RECIPE_BYTES,
            timeout=timeout,
        )
    except RemoteURLError as exc:
        raise RecipeURLError(str(exc)) from None
    except RemoteFetchError as exc:
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
