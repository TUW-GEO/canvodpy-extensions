"""canvod-filemap: naming recipes for non-canonical GNSS filenames."""

from importlib.metadata import version

__version__ = version("canvod-filemap")

from .mapping import VirtualFile
from .recipe import NamingRecipe, recipe_sha256
from .recipe_files import (
    RecipeNotFoundError,
    create_recipe,
    find_recipe,
    recipe_path,
)
from .remote import (
    RecipeFetchError,
    RecipeURLError,
    RemoteRecipeError,
    check_recipe_url,
    fetch_recipe,
    is_recipe_url,
)

__all__ = [
    "NamingRecipe",
    "RecipeFetchError",
    "RecipeNotFoundError",
    "RecipeURLError",
    "RemoteRecipeError",
    "VirtualFile",
    "check_recipe_url",
    "create_recipe",
    "fetch_recipe",
    "find_recipe",
    "is_recipe_url",
    "recipe_path",
    "recipe_sha256",
]
