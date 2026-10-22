"""Tests for recipes read from a URL (canvod.filemap.remote).

Downloads go to a local HTTP server, never to the network: the recipe URLs
stay ``https://raw.githubusercontent.com/...`` links and
``canvod.utils.remote_file._DOWNLOAD_ORIGIN`` sends the request to the server instead.
"""

from __future__ import annotations

import hashlib
import socket
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from canvod.filemap import (
    NamingRecipe,
    RecipeFetchError,
    RecipeURLError,
    RemoteRecipeError,
    check_recipe_url,
    fetch_recipe,
    find_recipe,
    is_recipe_url,
    recipe_sha256,
    remote,
)
from canvod.utils import remote_file, testing

COMMIT = "0123456789abcdef0123456789abcdef01234567"
REPO = "the-inklings/red-book"
NAME = f"{testing.SITE_KEY}_canopy"
FILE = f"recipes/{testing.SITE_KEY}/{NAME}.yaml"
COMMIT_URL = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{FILE}"
TAG_URL = f"https://raw.githubusercontent.com/{REPO}/refs/tags/v1/{FILE}"
BRANCH_URL = f"https://raw.githubusercontent.com/{REPO}/main/{FILE}"
TOKEN = "ghp_madeUpTokenOfTheInklings"

RECIPE = f"""\
name: {NAME}
description: {testing.CANOPY_SITE} canopy receiver
site: {testing.SITE_ID}
agency: {testing.AGENCY}
receiver_number: 1
receiver_type: canopy
sampling: 05S
period: 15M
content: AA
file_type: rnx
glob: "*.??o"
fields:
  - skip: 4
  - doy: 3
  - hour_letter: 1
  - minute: 2
  - skip: 1
  - yy: 2
  - skip: 1
""".encode()


class RecipeServer:
    """A local HTTP server: answers per path, records each request's headers."""

    def __init__(self) -> None:
        self.routes: dict[str, tuple[int, bytes, dict[str, str]]] = {}
        self.requests: list[tuple[str, dict[str, str]]] = []
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                server.requests.append((self.path, dict(self.headers)))
                status, body, headers = server.routes.get(self.path, (404, b"404: Not Found", {}))
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                pass

        # A larger backlog than the default 5: the parallel-fetch test connects 8 at once.
        server_class = type("Server", (ThreadingHTTPServer,), {"request_queue_size": 64})
        self.httpd = server_class(("127.0.0.1", 0), Handler)
        self.origin = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, args=(0.05,), daemon=True)
        self.thread.start()

    def serve(self, url: str, body: bytes, status: int = 200, **headers: str) -> None:
        self.routes[url.removeprefix("https://raw.githubusercontent.com")] = (
            status,
            body,
            headers,
        )

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


def _closed_origin() -> str:
    """An origin nothing listens on: a fetch from it fails like no network."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"


@pytest.fixture(autouse=True)
def _isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A new run with its folders in tmp_path, no token from the environment."""
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    _new_run(monkeypatch)
    for name in remote.TOKEN_VARIABLES:
        monkeypatch.delenv(name, raising=False)


def _new_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """A new run: a new run folder, nothing fetched yet.

    The variable is set (empty) through monkeypatch, so the value the run
    folder writes into it is undone after the test.
    """
    monkeypatch.setattr(remote_file, "_FOLDER", None)
    monkeypatch.setenv("CANVODPY_RUN_FOLDER", "")


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch):
    srv = RecipeServer()
    monkeypatch.setattr(remote_file, "_DOWNLOAD_ORIGIN", srv.origin)
    yield srv
    srv.close()


def _fetched_files() -> list[Path]:
    return sorted(p for p in remote_file.run_folder().rglob("*") if p.is_file())


# ---------------------------------------------------------------------------
# URL check
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (COMMIT_URL, True),
        ("HTTPS://raw.githubusercontent.com/a/b/c.yaml", True),
        ("http://raw.githubusercontent.com/a/b/c.yaml", True),
        (NAME, False),
        ("recipes/fangorn/fangorn_canopy.yaml", False),
    ],
)
def test_is_recipe_url(value: str, expected: bool) -> None:
    assert is_recipe_url(value) is expected


@pytest.mark.parametrize(
    "url",
    [
        COMMIT_URL,
        TAG_URL,
        TAG_URL.replace(".yaml", ".yml"),
        BRANCH_URL,
        f"https://raw.githubusercontent.com/{REPO}/refs/heads/main/{FILE}",
    ],
)
def test_commit_tag_and_branch_links_are_accepted(url: str) -> None:
    check_recipe_url(url)


def test_blob_link_is_refused_with_the_raw_link() -> None:
    blob = f"https://github.com/{REPO}/blob/{COMMIT}/{FILE}"
    with pytest.raises(RecipeURLError, match="raw link") as excinfo:
        check_recipe_url(blob)
    assert str(excinfo.value).endswith(COMMIT_URL)


@pytest.mark.parametrize(
    ("url", "match"),
    [
        (COMMIT_URL.replace("https://", "http://"), "https://"),
        (f"https://gitlab.com/{REPO}/{COMMIT}/{FILE}", "raw file link"),
        (f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/recipe.txt", r"\.yaml or \.yml"),
        (f"https://raw.githubusercontent.com/{REPO}/{COMMIT}", "<account>/<repo>"),
        (COMMIT_URL + "#L3", "fragment"),
    ],
)
def test_other_urls_are_refused(url: str, match: str) -> None:
    with pytest.raises(RecipeURLError, match=match):
        check_recipe_url(url)


def test_url_with_a_user_or_password_is_refused_without_showing_it() -> None:
    url = COMMIT_URL.replace("https://", f"https://tolkien:{TOKEN}@")
    with pytest.raises(RecipeURLError, match="GH_TOKEN") as excinfo:
        check_recipe_url(url)
    assert TOKEN not in str(excinfo.value)


def test_url_with_a_query_is_refused_without_showing_it() -> None:
    with pytest.raises(RecipeURLError, match="query") as excinfo:
        check_recipe_url(f"{COMMIT_URL}?token={TOKEN}")
    message = str(excinfo.value)
    assert TOKEN not in message
    assert COMMIT_URL in message


def test_url_errors_are_value_errors() -> None:
    assert issubclass(RecipeURLError, ValueError)
    assert issubclass(RecipeURLError, RemoteRecipeError)
    assert issubclass(RecipeFetchError, RemoteRecipeError)


def test_a_refused_url_is_never_requested(server: RecipeServer) -> None:
    with pytest.raises(RecipeURLError):
        fetch_recipe(f"https://raw.githubusercontent.com/{REPO}/main/recipe.txt")
    assert server.requests == []


# ---------------------------------------------------------------------------
# Fetch: once per run, again in every new run
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("url", [COMMIT_URL, TAG_URL, BRANCH_URL])
def test_fetched_recipe_loads(server: RecipeServer, url: str) -> None:
    server.serve(url, RECIPE)
    path = fetch_recipe(url)
    assert path.read_bytes() == RECIPE
    assert path.name == f"{NAME}.yaml"
    assert remote_file.run_folder() in path.parents
    recipe = NamingRecipe.load(path)
    assert recipe.name == NAME
    assert recipe.to_virtual_file(Path("rref001a15.25o")).canonical_str == (
        "FANA01INK_R_20250010015_15M_05S_AA.rnx"  # canopy receivers are "A"
    )
    assert server.requests[0][0] == url.removeprefix("https://raw.githubusercontent.com")


def test_recipe_sha256_is_that_of_the_served_bytes(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE)
    path = fetch_recipe(COMMIT_URL)
    expected = hashlib.sha256(RECIPE).hexdigest()
    assert recipe_sha256(path) == expected


def test_find_recipe_fetches_a_url(server: RecipeServer, tmp_path: Path) -> None:
    server.serve(COMMIT_URL, RECIPE)
    path = find_recipe(tmp_path / "config", testing.SITE_KEY, COMMIT_URL)
    assert path == fetch_recipe(COMMIT_URL)
    assert path.read_bytes() == RECIPE


def test_find_recipe_never_falls_back_to_a_local_recipe(
    server: RecipeServer, tmp_path: Path
) -> None:
    local = tmp_path / "recipes" / testing.SITE_KEY / f"{NAME}.yaml"
    local.parent.mkdir(parents=True)
    local.write_bytes(RECIPE)
    with pytest.raises(RecipeFetchError, match="not found"):
        find_recipe(tmp_path, testing.SITE_KEY, COMMIT_URL)


def test_a_run_fetches_a_recipe_once(server: RecipeServer) -> None:
    server.serve(BRANCH_URL, RECIPE)
    first = fetch_recipe(BRANCH_URL)
    assert fetch_recipe(BRANCH_URL) == first
    assert len(server.requests) == 1


def test_every_run_fetches_the_recipe_again(
    server: RecipeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    server.serve(BRANCH_URL, RECIPE)
    fetch_recipe(BRANCH_URL)
    moved = RECIPE.replace(b"receiver_number: 1", b"receiver_number: 2")
    server.serve(BRANCH_URL, moved)
    _new_run(monkeypatch)
    assert fetch_recipe(BRANCH_URL).read_bytes() == moved
    assert len(server.requests) == 2


def test_a_run_without_network_names_the_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(remote_file, "_DOWNLOAD_ORIGIN", _closed_origin())
    with pytest.raises(RecipeFetchError, match="needs network access") as excinfo:
        fetch_recipe(COMMIT_URL)
    assert COMMIT_URL in str(excinfo.value)
    assert _fetched_files() == []


def test_urls_are_kept_apart(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE)
    server.serve(TAG_URL, RECIPE)
    assert fetch_recipe(COMMIT_URL) != fetch_recipe(TAG_URL)
    assert len(_fetched_files()) == 2


def test_refused_replace_keeps_a_parallel_copy(
    server: RecipeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    # What Windows does when a parallel fetch holds the file open.
    server.serve(COMMIT_URL, RECIPE)

    def replace(src: str, dst: str) -> None:
        Path(dst).write_bytes(RECIPE)  # the parallel fetch's copy
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(remote_file.os, "replace", replace)
    path = fetch_recipe(COMMIT_URL)
    assert path.read_bytes() == RECIPE
    assert _fetched_files() == [path]


def test_refused_replace_without_a_copy_is_a_fetch_error(
    server: RecipeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    server.serve(COMMIT_URL, RECIPE)

    def replace(src: str, dst: str) -> None:
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(remote_file.os, "replace", replace)
    with pytest.raises(RecipeFetchError, match="Cannot write the fetched recipe"):
        fetch_recipe(COMMIT_URL)
    assert _fetched_files() == []


def test_parallel_fetches_give_one_complete_file(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE)
    paths: list[Path] = []
    errors: list[Exception] = []

    def fetch() -> None:
        try:
            paths.append(fetch_recipe(COMMIT_URL))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=fetch) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert len(set(paths)) == 1
    assert paths[0].read_bytes() == RECIPE


# ---------------------------------------------------------------------------
# Content checks: nothing is kept unless it is a valid recipe
# ---------------------------------------------------------------------------


def test_name_that_does_not_match_the_file_is_refused(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE.replace(f"name: {NAME}".encode(), b"name: orthanc_reference"))
    with pytest.raises(RecipeFetchError, match="orthanc_reference") as excinfo:
        fetch_recipe(COMMIT_URL)
    assert f"'{NAME}'" in str(excinfo.value)
    assert _fetched_files() == []


@pytest.mark.parametrize(
    ("body", "match"),
    [
        (b"name: [unclosed\n", "not a YAML file"),
        (b"\xff\xfe not text", "not a YAML file"),
        (f"name: {NAME}\nsite: {testing.SITE_ID}\n".encode(), "not a valid recipe"),
        (RECIPE.replace(b"- doy: 3", b"- dayofyear: 3"), "not a valid recipe"),
    ],
)
def test_invalid_recipe_is_refused(server: RecipeServer, body: bytes, match: str) -> None:
    server.serve(COMMIT_URL, body)
    with pytest.raises(RecipeFetchError, match=match) as excinfo:
        fetch_recipe(COMMIT_URL)
    assert COMMIT_URL in str(excinfo.value)
    assert _fetched_files() == []


def test_too_large_file_is_refused(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE + b"#" * remote.MAX_RECIPE_BYTES)
    with pytest.raises(RecipeFetchError, match="larger than"):
        fetch_recipe(COMMIT_URL)
    assert _fetched_files() == []


# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------


def _authorization(headers: dict[str, str]) -> str | None:
    return {k.lower(): v for k, v in headers.items()}.get("authorization")


def test_no_token_sends_no_authorization(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE)
    fetch_recipe(COMMIT_URL)
    assert _authorization(server.requests[0][1]) is None


@pytest.mark.parametrize("variable", ["GH_TOKEN", "GITHUB_TOKEN"])
def test_token_is_sent(
    server: RecipeServer, monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    monkeypatch.setenv(variable, TOKEN)
    server.serve(COMMIT_URL, RECIPE)
    fetch_recipe(COMMIT_URL)
    assert _authorization(server.requests[0][1]) == f"Bearer {TOKEN}"


def test_gh_token_comes_first(server: RecipeServer, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GH_TOKEN", TOKEN)
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_otherToken")
    server.serve(COMMIT_URL, RECIPE)
    fetch_recipe(COMMIT_URL)
    assert _authorization(server.requests[0][1]) == f"Bearer {TOKEN}"


def test_token_is_not_sent_to_a_redirect_target(
    server: RecipeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = RecipeServer()
    try:
        target.serve(COMMIT_URL, RECIPE)
        path = COMMIT_URL.removeprefix("https://raw.githubusercontent.com")
        server.serve(COMMIT_URL, b"", status=302, Location=target.origin + path)
        monkeypatch.setenv("GH_TOKEN", TOKEN)
        fetch_recipe(COMMIT_URL)
    finally:
        target.close()
    assert _authorization(server.requests[0][1]) == f"Bearer {TOKEN}"
    assert len(target.requests) == 1
    assert _authorization(target.requests[0][1]) is None


def test_private_recipe_without_token_names_the_variables(server: RecipeServer) -> None:
    with pytest.raises(RecipeFetchError, match="not found") as excinfo:
        fetch_recipe(COMMIT_URL)
    message = str(excinfo.value)
    assert COMMIT_URL in message
    assert "GH_TOKEN or GITHUB_TOKEN" in message


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500])
def test_token_never_appears_in_messages(
    server: RecipeServer, monkeypatch: pytest.MonkeyPatch, status: int
) -> None:
    monkeypatch.setenv("GH_TOKEN", TOKEN)
    server.serve(COMMIT_URL, b"no", status=status)
    with pytest.raises(RecipeFetchError) as excinfo:
        fetch_recipe(COMMIT_URL)
    assert TOKEN not in str(excinfo.value)
    assert excinfo.value.__cause__ is None
    assert f"HTTP {status}" in str(excinfo.value) or status == 404


@pytest.mark.parametrize(("status", "token"), [(403, None), (429, None), (401, TOKEN)])
def test_refused_requests_say_why(
    server: RecipeServer,
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    token: str | None,
) -> None:
    if token:
        monkeypatch.setenv("GH_TOKEN", token)
    server.serve(COMMIT_URL, b"no", status=status)
    with pytest.raises(RecipeFetchError, match="try again later"):
        fetch_recipe(COMMIT_URL)


# ---------------------------------------------------------------------------
# Unrecognized fields
# ---------------------------------------------------------------------------


def test_unrecognized_fields_are_named_in_file_order(tmp_path: Path) -> None:
    path = tmp_path / f"{NAME}.yaml"
    path.write_bytes(b"layout: '{site}/{yy}{doy}'\n" + RECIPE + b"recever_number: 2\n")
    assert NamingRecipe.unrecognized_fields(path) == ["layout", "recever_number"]
    recipe = NamingRecipe.load(path)
    assert recipe.receiver_number == 1


def test_known_recipe_has_no_unrecognized_fields(tmp_path: Path) -> None:
    path = tmp_path / f"{NAME}.yaml"
    path.write_bytes(RECIPE)
    assert NamingRecipe.unrecognized_fields(path) == []


def test_fetched_recipe_with_unrecognized_fields_still_loads(server: RecipeServer) -> None:
    server.serve(COMMIT_URL, RECIPE + b"layout: old\n")
    path = fetch_recipe(COMMIT_URL)
    assert NamingRecipe.unrecognized_fields(path) == ["layout"]
