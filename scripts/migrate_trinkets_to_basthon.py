"""One-off migration helper: snapshot embedded Trinkets and replace them with Basthon.

The script only touches pages that are part of _toc.yml. It downloads the saved
main.py for every embedded Trinket while Trinket is still online, stores the code
inside the repository, replaces the iframe/link with the local Basthon editor,
and removes Parsons problem blocks from the same live pages.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "docs" / "_static" / "basthon_examples"
REPORT_PATH = ROOT / "scripts" / "trinket_migration_report.json"
USER_AGENT = "Mozilla/5.0 (compatible; educational-content-migration/1.0)"

IFRAME_RE = re.compile(
    r'<iframe\b(?P<before>[^>]*?)src=["\'](?P<url>https?://(?:www\.)?trinket\.io/'
    r'embed/(?P<kind>python3|python|pygame)/(?P<id>[A-Za-z0-9]+)[^"\']*)["\']'
    r'(?P<after>[^>]*)>\s*</iframe>',
    re.IGNORECASE,
)
DIRECT_LINK_RE = re.compile(
    r'https?://(?:www\.)?trinket\.io/(?P<kind>python3|python|pygame)/'
    r'(?P<id>[A-Za-z0-9]+)(?![A-Za-z0-9])',
    re.IGNORECASE,
)
HEIGHT_RE = re.compile(r'\bheight=["\']?(\d+)', re.IGNORECASE)
LOCAL_FILE_PATTERNS = [
    re.compile(
        r'\b(?:open|loadtxt|genfromtxt|read_csv|read_table|read_json|imread|bgpic)'
        r'\s*\(\s*["\']([^"\']+)["\']'
    ),
    re.compile(r'\b(?:Image|PhotoImage)\s*\(\s*["\']([^"\']+)["\']'),
]

report: dict[str, object] = {
    "pages": [],
    "trinkets": {},
    "parsons_blocks_removed": 0,
    "warnings": [],
}
cache: dict[tuple[str, str], dict[str, object]] = {}


def toc_sources() -> list[Path]:
    toc = (ROOT / "_toc.yml").read_text(encoding="utf-8")
    stems: list[str] = []
    root_match = re.search(r"(?m)^root:\s*([^#\s]+)", toc)
    if root_match:
        stems.append(root_match.group(1))
    stems.extend(re.findall(r"(?m)^\s*-\s*file:\s*([^#\s]+)", toc))

    files: list[Path] = []
    for stem in dict.fromkeys(stems):
        base = ROOT / stem
        candidates = [base] if base.suffix else [base.with_suffix(ext) for ext in (".ipynb", ".md", ".rst")]
        for candidate in candidates:
            if candidate.exists():
                files.append(candidate)
                break
        else:
            report["warnings"].append(f"TOC source not found: {stem}")
    return files


def fetch_bytes(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "")
    return data, content_type


def fetch_main(kind: str, trinket_id: str) -> tuple[str, str]:
    candidates = [
        f"https://trinket.io/{kind}/{trinket_id}/main.py",
        f"https://www.trinket.io/{kind}/{trinket_id}/main.py",
        f"https://trinket.io/embed/{kind}/{trinket_id}/main.py",
    ]
    errors: list[str] = []
    for url in candidates:
        try:
            raw, content_type = fetch_bytes(url)
            text = raw.decode("utf-8-sig")
            beginning = text.lstrip().lower()[:100]
            if not text.strip() or beginning.startswith("<!doctype") or beginning.startswith("<html"):
                raise ValueError(f"received HTML/empty response ({content_type})")
            return text, url
        except (OSError, UnicodeError, ValueError, urllib.error.URLError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Could not download main.py; " + " | ".join(errors))


def infer_local_files(source: str) -> list[str]:
    names: list[str] = []
    for pattern in LOCAL_FILE_PATTERNS:
        for match in pattern.finditer(source):
            name = match.group(1).strip()
            if not name or "://" in name or name.startswith(("/", "~")):
                continue
            # Only migrate simple repository-like filenames. Dynamic paths and
            # parent traversal are intentionally ignored and reported later.
            if ".." in Path(name).parts:
                continue
            if name not in names:
                names.append(name)
    return names


def fetch_auxiliary(kind: str, trinket_id: str, filename: str) -> tuple[bytes, str] | None:
    encoded = "/".join(urllib.parse.quote(part) for part in Path(filename).parts)
    candidates = [
        f"https://trinket.io/{kind}/{trinket_id}/{encoded}",
        f"https://www.trinket.io/{kind}/{trinket_id}/{encoded}",
        f"https://trinket.io/embed/{kind}/{trinket_id}/{encoded}",
    ]
    for url in candidates:
        try:
            raw, content_type = fetch_bytes(url)
            if not raw:
                continue
            if content_type.startswith("text/html") and raw.lstrip().lower().startswith((b"<!doctype", b"<html")):
                continue
            return raw, url
        except (OSError, urllib.error.URLError):
            continue
    return None


def snapshot(kind: str, trinket_id: str) -> dict[str, object]:
    key = (kind.lower(), trinket_id)
    if key in cache:
        return cache[key]

    source, source_url = fetch_main(kind, trinket_id)
    directory = EXAMPLES / f"trinket_{trinket_id}"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "main.py").write_text(source, encoding="utf-8")

    auxiliaries: list[str] = []
    missing_auxiliaries: list[str] = []
    auxiliary_sources: dict[str, str] = {}
    for name in infer_local_files(source):
        result = fetch_auxiliary(kind, trinket_id, name)
        if result is None:
            missing_auxiliaries.append(name)
            continue
        raw, aux_url = result
        destination = directory / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        auxiliaries.append(name)
        auxiliary_sources[name] = aux_url

    syntax_error = None
    try:
        compile(source, str(directory / "main.py"), "exec")
    except SyntaxError as exc:
        syntax_error = f"{exc.msg} (line {exc.lineno})"

    item: dict[str, object] = {
        "kind": kind,
        "id": trinket_id,
        "source_url": source_url,
        "local_main": str((directory / "main.py").relative_to(ROOT)),
        "auxiliaries": auxiliaries,
        "auxiliary_sources": auxiliary_sources,
        "missing_auxiliaries": missing_auxiliaries,
        "syntax_error": syntax_error,
    }
    cache[key] = item
    report["trinkets"][trinket_id] = item
    if missing_auxiliaries:
        report["warnings"].append(
            f"Trinket {trinket_id}: could not snapshot referenced files: {', '.join(missing_auxiliaries)}"
        )
    if syntax_error:
        report["warnings"].append(f"Trinket {trinket_id}: Python syntax warning: {syntax_error}")
    return item


def relative_basthon_prefix(source_path: Path) -> str:
    relative = source_path.relative_to(ROOT)
    depth = len(relative.parent.parts)
    return "../" * depth + "basthon/"


def basthon_url(source_path: Path, item: dict[str, object]) -> str:
    trinket_id = str(item["id"])
    path = f"examples/trinket_{trinket_id}/main.py"
    params: list[tuple[str, str]] = [("from", path)]
    for filename in item["auxiliaries"]:
        aux_path = f"examples/trinket_{trinket_id}/{filename}"
        if str(filename).lower().endswith(".py"):
            params.append(("module", aux_path))
        else:
            params.append(("aux", aux_path))
    query = urllib.parse.urlencode(params)
    return relative_basthon_prefix(source_path) + "?" + query


def replace_trinkets(text: str, source_path: Path) -> tuple[str, int]:
    count = 0

    def iframe_repl(match: re.Match[str]) -> str:
        nonlocal count
        kind = match.group("kind").lower()
        trinket_id = match.group("id")
        item = snapshot(kind, trinket_id)
        height_match = HEIGHT_RE.search(match.group(0))
        height = height_match.group(1) if height_match else "600"
        count += 1
        return (
            f'<iframe src="{basthon_url(source_path, item)}" width="100%" height="{height}" '
            'frameborder="0" title="Interaktiv Python-editor" loading="lazy" allowfullscreen></iframe>'
        )

    text = IFRAME_RE.sub(iframe_repl, text)

    def link_repl(match: re.Match[str]) -> str:
        nonlocal count
        kind = match.group("kind").lower()
        trinket_id = match.group("id")
        item = snapshot(kind, trinket_id)
        count += 1
        return basthon_url(source_path, item)

    # Some older pages link to a Trinket rather than embedding it. Migrate those
    # links too so no live page depends on trinket.io after shutdown.
    text = DIRECT_LINK_RE.sub(link_repl, text)
    return text, count


def directive_spans(lines: list[str]) -> list[tuple[int, int]]:
    stack: list[tuple[int, int]] = []
    spans: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        opener = re.match(r"^\s*(`{3,})\{", line)
        if opener:
            stack.append((len(opener.group(1)), index))
            continue
        closer = re.match(r"^\s*(`{3,})\s*$", line)
        if not closer:
            continue
        length = len(closer.group(1))
        for position in range(len(stack) - 1, -1, -1):
            if stack[position][0] == length:
                _, start = stack.pop(position)
                spans.append((start, index))
                break
    return spans


def remove_parsons(text: str) -> tuple[str, int]:
    if "parsons" not in text.lower():
        return text, 0

    lines = text.splitlines(keepends=True)
    spans = directive_spans(lines)
    remove_ranges: set[tuple[int, int]] = set()
    loose_lines: set[int] = set()

    for index, line in enumerate(lines):
        if "parsons" not in line.lower():
            continue
        containing = [span for span in spans if span[0] <= index <= span[1]]
        if containing:
            # Remove the smallest (innermost) MyST block containing the Parsons link.
            remove_ranges.add(min(containing, key=lambda span: span[1] - span[0]))
        else:
            loose_lines.add(index)

    indices: set[int] = set(loose_lines)
    for start, end in remove_ranges:
        indices.update(range(start, end + 1))

    if not indices:
        return text, 0

    cleaned = "".join(line for idx, line in enumerate(lines) if idx not in indices)
    removed = len(remove_ranges) + len(loose_lines)
    return cleaned, removed


def update_notebook(path: Path) -> tuple[int, int]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    trinkets = 0
    parsons = 0
    new_cells = []

    for cell in notebook.get("cells", []):
        source = cell.get("source", [])
        text = "".join(source) if isinstance(source, list) else str(source)

        if cell.get("cell_type") == "markdown":
            text, replaced = replace_trinkets(text, path)
            trinkets += replaced
            text, removed = remove_parsons(text)
            parsons += removed
            if "parsons" in text.lower():
                report["warnings"].append(f"Parsons text remains in {path.relative_to(ROOT)}")
            cell["source"] = text.splitlines(keepends=True)
            if text.strip():
                new_cells.append(cell)
        else:
            if "parsons" in text.lower():
                parsons += 1
                continue
            new_cells.append(cell)

    notebook["cells"] = new_cells
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return trinkets, parsons


def update_text_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    text, trinkets = replace_trinkets(text, path)
    text, parsons = remove_parsons(text)
    path.write_text(text, encoding="utf-8")
    return trinkets, parsons


def validate(files: list[Path]) -> None:
    errors: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        if "trinket.io" in text:
            errors.append(f"Trinket URL remains in {path.relative_to(ROOT)}")
        if "parsons.problemsolving.io" in text:
            errors.append(f"Parsons URL remains in {path.relative_to(ROOT)}")
        if path.suffix == ".ipynb":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid notebook JSON in {path.relative_to(ROOT)}: {exc}")
    if errors:
        raise RuntimeError("Migration validation failed:\n- " + "\n- ".join(errors))


def main() -> None:
    files = toc_sources()
    if not files:
        raise SystemExit("No live source files found from _toc.yml")

    EXAMPLES.mkdir(parents=True, exist_ok=True)
    total_trinkets = 0
    total_parsons = 0

    for path in files:
        if path.suffix == ".ipynb":
            trinkets, parsons = update_notebook(path)
        else:
            trinkets, parsons = update_text_file(path)
        if trinkets or parsons:
            report["pages"].append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "trinket_references_replaced": trinkets,
                    "parsons_blocks_removed": parsons,
                }
            )
        total_trinkets += trinkets
        total_parsons += parsons

    report["trinket_references_replaced"] = total_trinkets
    report["unique_trinkets_snapshotted"] = len(cache)
    report["parsons_blocks_removed"] = total_parsons
    validate(files)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Replaced {total_trinkets} Trinket references ({len(cache)} unique Trinkets).")
    print(f"Removed {total_parsons} Parsons blocks/references.")
    if report["warnings"]:
        print("Warnings:")
        for warning in report["warnings"]:
            print(" -", warning)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
