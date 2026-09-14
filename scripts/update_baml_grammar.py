#!/usr/bin/env python3
"""Synchronize the pinned BAML Tree-sitter grammar and Zed query files."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "extension.toml"
LANGUAGE_DIR = ROOT / "languages" / "baml"
UPSTREAM_REPOSITORY = "https://github.com/BoundaryML/baml-treesitter"
LATEST_COMMIT_API = "https://api.github.com/repos/BoundaryML/baml-treesitter/commits/main"
RAW_BASE_URL = "https://raw.githubusercontent.com/BoundaryML/baml-treesitter"
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")

CAPTURE_ADAPTATIONS = (
    ("@comment.documentation", "@comment.doc"),
    ("@keyword.control", "@keyword"),
    ("@keyword.operator", "@operator"),
    ("@function.method", "@function"),
    ("@variable.builtin", "@variable.special"),
    ("@module", "@variable.special"),
)

SUPPORTED_ZED_CAPTURES = {
    "@attribute",
    "@boolean",
    "@comment",
    "@comment.doc",
    "@constant",
    "@constant.builtin",
    "@constructor",
    "@embedded",
    "@emphasis",
    "@emphasis.strong",
    "@enum",
    "@function",
    "@hint",
    "@keyword",
    "@label",
    "@link_text",
    "@link_uri",
    "@number",
    "@operator",
    "@predictive",
    "@preproc",
    "@primary",
    "@property",
    "@punctuation",
    "@punctuation.bracket",
    "@punctuation.delimiter",
    "@punctuation.list_marker",
    "@punctuation.special",
    "@string",
    "@string.escape",
    "@string.regex",
    "@string.special",
    "@string.special.symbol",
    "@tag",
    "@tag.doctype",
    "@text.literal",
    "@title",
    "@type",
    "@type.builtin",
    "@variable",
    "@variable.parameter",
    "@variable.special",
    "@variant",
}


def fetch_text(url: str) -> str:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "baml-lsp-zed-extension",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def latest_revision() -> str:
    revision = json.loads(fetch_text(LATEST_COMMIT_API))["sha"]
    if not SHA_PATTERN.fullmatch(revision):
        raise ValueError(f"GitHub returned an invalid commit SHA: {revision!r}")
    return revision


def remove_upstream_header(source: str) -> str:
    lines = source.splitlines()
    index = 0
    while index < len(lines) and lines[index].startswith(";"):
        index += 1
    if index < len(lines) and not lines[index]:
        index += 1
    return "\n".join(lines[index:]).rstrip() + "\n"


def adapt_highlights(source: str, revision: str) -> str:
    adapted = remove_upstream_header(source)
    for upstream_capture, zed_capture in CAPTURE_ADAPTATIONS:
        adapted = adapted.replace(upstream_capture, zed_capture)

    result = (
        "; BAML highlight queries adapted for Zed from BoundaryML/baml-treesitter.\n"
        f"; Grammar revision: {revision}.\n\n"
        f"{adapted}"
    )
    validate_zed_captures(result)
    return result


def adapt_injections(source: str, revision: str) -> str:
    return (
        "; Adapted for Zed from BoundaryML/baml-treesitter.\n"
        f"; Grammar revision: {revision}.\n\n"
        f"{source.lstrip()}"
    )


def validate_zed_captures(query: str) -> None:
    query_without_comments = "\n".join(
        line.split(";", 1)[0] for line in query.splitlines()
    )
    captures = set(re.findall(r"@[A-Za-z][A-Za-z0-9_.-]*", query_without_comments))
    unsupported = sorted(captures - SUPPORTED_ZED_CAPTURES)
    if unsupported:
        joined = ", ".join(unsupported)
        raise ValueError(f"Unsupported Zed highlight captures: {joined}")


def update_manifest(revision: str) -> tuple[bool, str]:
    text = MANIFEST.read_text()
    grammar_pattern = re.compile(
        r'(\[grammars\.baml\]\n'
        rf'repository = "{re.escape(UPSTREAM_REPOSITORY)}"\n'
        r'rev = ")[0-9a-f]{40}("\n)'
    )
    match = grammar_pattern.search(text)
    if not match:
        raise ValueError("Could not find the BAML grammar pin in extension.toml")

    current_revision = SHA_PATTERN.search(match.group(0))
    if current_revision is None:
        raise ValueError("Could not read the current BAML grammar revision")
    if current_revision.group(0) == revision:
        version = re.search(r'^version = "([0-9]+\.[0-9]+\.[0-9]+)"$', text, re.MULTILINE)
        if version is None:
            raise ValueError("Could not read the extension version")
        return False, version.group(1)

    text = grammar_pattern.sub(rf"\g<1>{revision}\g<2>", text, count=1)

    version_pattern = re.compile(r'^version = "([0-9]+)\.([0-9]+)\.([0-9]+)"$', re.MULTILINE)
    version_match = version_pattern.search(text)
    if version_match is None:
        raise ValueError("Could not find a semantic extension version")
    major, minor, patch = (int(part) for part in version_match.groups())
    next_version = f"{major}.{minor}.{patch + 1}"
    text = version_pattern.sub(f'version = "{next_version}"', text, count=1)
    MANIFEST.write_text(text)
    return True, next_version


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text() == content:
        return False
    path.write_text(content)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rev",
        help="Use a specific 40-character commit SHA instead of the latest main commit",
    )
    args = parser.parse_args()

    revision = args.rev or latest_revision()
    if not SHA_PATTERN.fullmatch(revision):
        parser.error("--rev must be a full 40-character lowercase commit SHA")

    highlights_source = fetch_text(f"{RAW_BASE_URL}/{revision}/queries/highlights.scm")
    injections_source = fetch_text(f"{RAW_BASE_URL}/{revision}/queries/injections.scm")
    highlights = adapt_highlights(highlights_source, revision)
    injections = adapt_injections(injections_source, revision)

    manifest_changed, version = update_manifest(revision)
    highlights_changed = write_if_changed(LANGUAGE_DIR / "highlights.scm", highlights)
    injections_changed = write_if_changed(LANGUAGE_DIR / "injections.scm", injections)

    changed = manifest_changed or highlights_changed or injections_changed
    state = "updated" if changed else "already current"
    print(f"BAML grammar {state}: {revision} (extension {version})")


if __name__ == "__main__":
    main()
