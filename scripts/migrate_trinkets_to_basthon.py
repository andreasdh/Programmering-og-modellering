"""One-off migration: snapshot live Trinkets, replace them with Basthon, remove Parsons."""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "docs" / "_static" / "basthon_examples"
REPORT_PATH = ROOT / "scripts" / "trinket_migration_report.json"
USER_AGENT = "Mozilla/5.0 (educational-content-migration)"

IFRAME_RE = re.compile(
    r'<iframe\b[^>]*?src=["\']https?://(?:www\.)?trinket\.io/embed/'
    r'(?P<kind>python3|python|pygame)/(?P<id>[A-Za-z0-9]+)[^"\']*["\'][^>]*>'
    r'\s*</iframe>', re.IGNORECASE,
)
LINK_RE = re.compile(
    r'https?://(?:www\.)?trinket\.io/(?:embed/)?(?P<kind>python3|python|pygame)/'
    r'(?P<id>[A-Za-z0-9]+)(?:\?[^\s)\]"\']*)?', re.IGNORECASE,
)
HEIGHT_RE = re.compile(r'\bheight=["\']?(\d+)', re.IGNORECASE)
PROJECT_RE = re.compile(r'trinketObject\s*=\s*(\{.*?\});\s*(?:\r?\n\s*)*draftObject', re.DOTALL)

report = {"pages": [], "trinkets": {}, "warnings": []}
cache: dict[tuple[str, str], dict] = {}


def toc_sources() -> list[Path]:
    toc = (ROOT / "_toc.yml").read_text(encoding="utf-8")
    stems = []
    root = re.search(r"(?m)^root:\s*([^#\s]+)", toc)
    if root:
        stems.append(root.group(1))
    stems += re.findall(r"(?m)^\s*-\s*file:\s*([^#\s]+)", toc)
    files = []
    for stem in dict.fromkeys(stems):
        base = ROOT / stem
        candidates = [base] if base.suffix else [base.with_suffix(x) for x in (".ipynb", ".md", ".rst")]
        match = next((p for p in candidates if p.exists()), None)
        if match:
            files.append(match)
        else:
            report["warnings"].append(f"TOC source not found: {stem}")
    return files


def get_bytes(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read(), response.headers.get("Content-Type", "")


def get_project(kind: str, trinket_id: str) -> tuple[dict, str]:
    url = f"https://trinket.io/embed/{kind}/{trinket_id}"
    raw, _ = get_bytes(url)
    page = raw.decode("utf-8", errors="replace")
    match = PROJECT_RE.search(page)
    if not match:
        raise RuntimeError(f"Could not find trinketObject in {url}")
    project = json.loads(match.group(1))
    return project, url


def safe_name(name: str) -> str | None:
    name = name.replace("\\", "/").lstrip("/")
    path = Path(name)
    if not name or ".." in path.parts:
        return None
    return name


def extract_files(project: dict) -> list[dict]:
    encoded = project.get("code") or "[]"
    try:
        files = json.loads(html.unescape(encoded)) if isinstance(encoded, str) else encoded
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not decode Trinket code payload: {exc}") from exc
    result = []
    for item in files or []:
        if not isinstance(item, dict):
            continue
        name = safe_name(str(item.get("name") or ""))
        if not name:
            continue
        result.append({"name": name, "content": str(item.get("content") or "")})
    if not result:
        result = [{"name": "main.py", "content": ""}]
    return result


def snapshot(kind: str, trinket_id: str) -> dict:
    key = (kind.lower(), trinket_id)
    if key in cache:
        return cache[key]

    project, source_url = get_project(kind, trinket_id)
    files = extract_files(project)
    directory = EXAMPLES / f"trinket_{trinket_id}"
    directory.mkdir(parents=True, exist_ok=True)

    names = []
    for item in files:
        destination = directory / item["name"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(item["content"], encoding="utf-8")
        names.append(item["name"])

    main_name = "main.py" if "main.py" in names else next((x for x in names if x.endswith(".py")), names[0])
    main_source = (directory / main_name).read_text(encoding="utf-8")
    syntax_error = None
    if main_name.endswith(".py"):
        try:
            compile(main_source, str(directory / main_name), "exec")
        except SyntaxError as exc:
            syntax_error = f"{exc.msg} (line {exc.lineno})"
            report["warnings"].append(f"Trinket {trinket_id}: syntax warning: {syntax_error}")

    assets = project.get("assets") or []
    if assets:
        report["warnings"].append(
            f"Trinket {trinket_id} ({project.get('name') or ''}) has {len(assets)} separate asset(s); inspect if used."
        )

    item = {
        "id": trinket_id,
        "kind": kind,
        "name": project.get("name"),
        "source_url": source_url,
        "main": main_name,
        "files": names,
        "asset_count": len(assets),
        "assets": assets,
        "syntax_error": syntax_error,
    }
    cache[key] = item
    report["trinkets"][trinket_id] = item
    return item


def basthon_prefix(source_path: Path) -> str:
    depth = len(source_path.relative_to(ROOT).parent.parts)
    return "../" * depth + "basthon/"


def basthon_url(source_path: Path, item: dict) -> str:
    folder = f"examples/trinket_{item['id']}/"
    params = [("from", folder + item["main"])]
    for name in item["files"]:
        if name == item["main"]:
            continue
        params.append(("module" if name.lower().endswith(".py") else "aux", folder + name))
    return basthon_prefix(source_path) + "?" + urllib.parse.urlencode(params)


def replace_trinkets(text: str, source_path: Path) -> tuple[str, int]:
    count = 0

    def iframe(match: re.Match) -> str:
        nonlocal count
        item = snapshot(match.group("kind").lower(), match.group("id"))
        height_match = HEIGHT_RE.search(match.group(0))
        height = height_match.group(1) if height_match else "600"
        count += 1
        return (
            f'<iframe src="{basthon_url(source_path, item)}" width="100%" height="{height}" '
            'frameborder="0" title="Interaktiv Python-editor" loading="lazy" allowfullscreen></iframe>'
        )

    text = IFRAME_RE.sub(iframe, text)

    def link(match: re.Match) -> str:
        nonlocal count
        item = snapshot(match.group("kind").lower(), match.group("id"))
        count += 1
        return basthon_url(source_path, item)

    text = LINK_RE.sub(link, text)
    return text, count


def directive_spans(lines: list[str]) -> list[tuple[int, int]]:
    stack, spans = [], []
    for i, line in enumerate(lines):
        opening = re.match(r"^\s*(`{3,})\{", line)
        if opening:
            stack.append((len(opening.group(1)), i))
            continue
        closing = re.match(r"^\s*(`{3,})\s*$", line)
        if not closing:
            continue
        length = len(closing.group(1))
        for pos in range(len(stack) - 1, -1, -1):
            if stack[pos][0] == length:
                _, start = stack.pop(pos)
                spans.append((start, i))
                break
    return spans


def remove_parsons(text: str) -> tuple[str, int]:
    if "parsons" not in text.lower():
        return text, 0
    lines = text.splitlines(keepends=True)
    spans = directive_spans(lines)
    ranges, loose = set(), set()
    for i, line in enumerate(lines):
        if "parsons" not in line.lower():
            continue
        containing = [span for span in spans if span[0] <= i <= span[1]]
        if containing:
            ranges.add(min(containing, key=lambda span: span[1] - span[0]))
        else:
            loose.add(i)
    remove = set(loose)
    for start, end in ranges:
        remove.update(range(start, end + 1))
    return "".join(line for i, line in enumerate(lines) if i not in remove), len(ranges) + len(loose)


def update_notebook(path: Path) -> tuple[int, int]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    trinkets = parsons = 0
    cells = []
    for cell in notebook.get("cells", []):
        source = cell.get("source", [])
        text = "".join(source) if isinstance(source, list) else str(source)
        if cell.get("cell_type") == "markdown":
            text, n = replace_trinkets(text, path)
            trinkets += n
            text, n = remove_parsons(text)
            parsons += n
            cell["source"] = text.splitlines(keepends=True)
            if text.strip():
                cells.append(cell)
        elif "parsons" not in text.lower():
            cells.append(cell)
        else:
            parsons += 1
    notebook["cells"] = cells
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return trinkets, parsons


def update_text(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    text, trinkets = replace_trinkets(text, path)
    text, parsons = remove_parsons(text)
    path.write_text(text, encoding="utf-8")
    return trinkets, parsons


def validate(files: list[Path]) -> None:
    errors = []
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
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    total_trinkets = total_parsons = 0
    for path in files:
        trinkets, parsons = update_notebook(path) if path.suffix == ".ipynb" else update_text(path)
        if trinkets or parsons:
            report["pages"].append({
                "path": str(path.relative_to(ROOT)),
                "trinket_references_replaced": trinkets,
                "parsons_blocks_removed": parsons,
            })
        total_trinkets += trinkets
        total_parsons += parsons
    report["trinket_references_replaced"] = total_trinkets
    report["unique_trinkets_snapshotted"] = len(cache)
    report["parsons_blocks_removed"] = total_parsons
    validate(files)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Replaced {total_trinkets} Trinket references ({len(cache)} unique projects).")
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
