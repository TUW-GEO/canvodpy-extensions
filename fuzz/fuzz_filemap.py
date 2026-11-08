"""Fuzz canvod-filemap: naming recipes read from YAML, file names read with a recipe.

One input is one case. Its first byte picks the target, the rest is the
text (UTF-8, invalid bytes replaced):

- even first byte: the text is a recipe file (``NamingRecipe.from_yaml``)
- odd first byte: the text is a file name, read with one of two fixed
  recipes (``NamingRecipe.matches``, then ``NamingRecipe.to_virtual_file``)

Bad input must end in an error the code documents for it: ``yaml.YAMLError``
or ``ValueError`` (pydantic's ``ValidationError`` is one). Any other
exception is a bug, and so is a hang or a memory blow-up (the fuzzer's
``-timeout`` and ``-rss_limit_mb``).

Run with ``just fuzz filemap`` (Linux x86_64 only: atheris has no other
wheels). The tests replay the saved inputs in ``fuzz/corpus/filemap`` and
``fuzz/crashes/filemap`` on every platform, without atheris
(``fuzz/tests/test_fuzz_replay.py``).
"""

import sys
from pathlib import Path

import yaml
from canvod.filemap.recipe import NamingRecipe

#: Short RINEX names with a session letter and minutes: ract001a15.25o
_SHORT = NamingRecipe(
    name="fuzz_short",
    site="FAN",
    agency="INK",
    receiver_number=1,
    glob="*",
    fields=[
        {"skip": 4},
        {"doy": 3},
        {"hour_letter": 1},
        {"minute": 2},
        {"skip": 1},
        {"yy": 2},
        {"skip": 1},
    ],
)

#: Names with a full date and time: FAN_2025_001_1530.dat
_LONG = NamingRecipe(
    name="fuzz_long",
    site="FAN",
    agency="INK",
    receiver_number=1,
    glob="*",
    fields=[
        {"skip": 4},
        {"year": 4},
        {"skip": 1},
        {"doy": 3},
        {"skip": 1},
        {"hour": 2},
        {"minute": 2},
        {"skip": 4},
    ],
)


def fuzz_one_input(data: bytes) -> None:
    """Run one fuzz input; raise only for a bug."""
    if not data:
        return
    text = data[1:].decode("utf-8", errors="replace")
    try:
        if data[0] % 2 == 0:
            NamingRecipe.from_yaml(text)
        else:
            recipe = _SHORT if data[0] % 4 == 1 else _LONG
            # A file name, never a path
            name = text.replace("/", "_").replace("\\", "_")
            if recipe.matches(name):
                recipe.to_virtual_file(Path(name))
    except yaml.YAMLError, ValueError:
        pass


def main() -> None:
    """Fuzz with atheris; the arguments go to libFuzzer."""
    try:
        import atheris
    except ImportError:
        sys.exit("atheris runs on Linux x86_64 only: uv sync --group fuzz there")
    atheris.instrument_all()
    atheris.Setup(sys.argv, fuzz_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
