"""Build the contributor index from accepted Open Colab research records."""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
import sys
from tempfile import NamedTemporaryFile
from urllib.parse import quote


ROLES = {
    "proposal",
    "experiment",
    "analysis",
    "implementation",
    "peer review",
    "reproduction",
    "replication",
    "improvement",
    "synthesis",
    "cross-discovery",
}
OUTCOME_GROUPS = ("verified-findings", "negative-results", "cross-discoveries")
RECORD_GROUPS = ("proposals", "experiments", *OUTCOME_GROUPS)
HANDLE = re.compile(r"[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*")
MARKER = re.compile(r"^[ \t]*<!--[ \t]*open-colab-credit\b", re.MULTILINE)
BLOCK = re.compile(
    r"^<!-- open-colab-credit[ \t]*\n(.*?)\n-->[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True, order=True)
class Credit:
    handle: str
    role: str
    agent: str


@dataclass(frozen=True)
class Record:
    contributors: tuple[Credit, ...] = ()
    builds_on: tuple[str, ...] = ()


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def parse_credit(entry):
    if not isinstance(entry, dict) or entry.keys() - {"handle", "role", "agent"}:
        raise ValueError("each contributor must have handle, role and optional agent fields")
    handle = entry.get("handle")
    role = entry.get("role")
    agent = entry.get("agent", "")
    if not isinstance(handle, str) or len(handle) > 39 or not HANDLE.fullmatch(handle):
        raise ValueError("expected a GitHub handle without the @ prefix")
    if not isinstance(role, str) or role not in ROLES:
        raise ValueError("unrecognized contributor role")
    if "agent" in entry and (
        not isinstance(agent, str) or not agent.strip() or not agent.isprintable()
    ):
        raise ValueError("agent must be a printable display name")
    return Credit(handle.lower(), role, agent.strip())


def parse_record(content):
    markers = MARKER.findall(content)
    if not markers:
        return Record()
    match = BLOCK.search(content)
    if len(markers) != 1 or match is None:
        raise ValueError("expected one open-colab-credit comment with its own opening and closing lines")
    metadata = json.loads(match.group(1), object_pairs_hook=unique_json_object)
    if not isinstance(metadata, dict) or metadata.keys() - {"contributors", "builds_on"}:
        raise ValueError("credit must be a JSON object with contributors and/or builds_on")
    entries = metadata.get("contributors", [])
    sources = metadata.get("builds_on", [])
    if not isinstance(entries, list):
        raise ValueError("contributors must be a list")
    if not isinstance(sources, list) or any(not isinstance(source, str) for source in sources):
        raise ValueError("builds_on must be a list of repository-relative record paths")
    return Record(tuple(sorted(set(map(parse_credit, entries)))), tuple(sorted(set(sources))))


def load_records(root):
    research = root / "research"
    if research.is_symlink():
        raise ValueError("research must be a directory inside the repository")

    records = {}
    for group in RECORD_GROUPS:
        directory = research / group
        if directory.is_symlink():
            raise ValueError(f"research/{group} must be a directory inside the repository")
        if not directory.exists():
            continue
        for item in sorted(directory.iterdir()):
            if item.is_symlink():
                raise ValueError(f"{item.relative_to(root).as_posix()} is a symbolic link")
            path = item / "README.md" if item.is_dir() else item
            if path.suffix != ".md":
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ValueError(f"{relative} is a symbolic link")
            if path.is_file():
                try:
                    records[relative] = parse_record(path.read_text(encoding="utf-8-sig"))
                except (OSError, ValueError) as error:
                    raise ValueError(f"{relative}: {error}") from error
    return records


def collect_credits(records):
    """Resolve each record's direct credits and the credits of its declared sources."""
    resolved = {}
    active = []
    visiting = set()

    def visit(path):
        if path in resolved:
            return resolved[path]
        if path in visiting:
            cycle = " -> ".join([*active[active.index(path) :], path])
            raise ValueError(f"credit cycle: {cycle}")
        active.append(path)
        visiting.add(path)
        record = records[path]
        credits = {(credit, path) for credit in record.contributors}
        for source in record.builds_on:
            if source not in records:
                raise ValueError(f"{path}: builds_on record does not exist: {source!r}")
            credits.update(visit(source))
        active.pop()
        visiting.remove(path)
        resolved[path] = credits
        return credits

    for path in sorted(records):
        visit(path)
    return resolved


def markdown_text(value):
    escaped = re.sub(r"([\\`*_\[\]{}()#!|~])", r"\\\1", value)
    return escape(escaped).replace("@", "&#64;")


def record_link(path):
    label = path.removeprefix("research/").removesuffix(".md").removesuffix("/README")
    return f"[{markdown_text(label)}]({quote(path)})"


def credit_lines(contributions):
    by_handle = defaultdict(list)
    for credit, path in sorted(contributions):
        label = f"{credit.role} ({markdown_text(credit.agent)})" if credit.agent else credit.role
        by_handle[credit.handle].append(f"{label} on {record_link(path)}")
    return [
        f"- [{handle}](https://github.com/{handle}) · {', '.join(roles)}"
        for handle, roles in by_handle.items()
    ]


def render(records, resolved):
    lines = [
        "# Contributors",
        "",
        "<!-- Generated by tools/update_credits.py. Edit the research records to change credits. -->",
        "",
        "Credits list the public handles and roles recorded in accepted research contributions.",
        "",
        "## Contributions",
        "",
    ]
    direct = {(credit, path) for path, record in records.items() for credit in record.contributors}
    lines.extend(credit_lines(direct) or ["No public contributor credits recorded yet."])
    lines.extend(["", "## Credit by outcome", ""])
    outcomes = [
        path for path in sorted(records) if PurePosixPath(path).parts[1] in OUTCOME_GROUPS
    ]
    if not outcomes:
        lines.append("No research outcomes recorded yet.")
    for path in outcomes:
        lines.extend([f"### {record_link(path)}", ""])
        lines.extend(credit_lines(resolved[path]) or ["No public contributor credits recorded."])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update(root, check):
    records = load_records(root)
    expected = render(records, collect_credits(records)).encode("utf-8")
    output = root / "CONTRIBUTORS.md"
    if output.is_symlink():
        raise ValueError("CONTRIBUTORS.md is a symbolic link")
    if output.is_file() and output.read_bytes().replace(b"\r\n", b"\n") == expected:
        return
    if check:
        raise ValueError("CONTRIBUTORS.md is missing or stale. Run python tools/update_credits.py.")

    with NamedTemporaryFile(dir=root, delete=False) as temp:
        temporary = Path(temp.name)
    try:
        temporary.write_bytes(expected)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check the index without writing it")
    args = parser.parse_args()
    try:
        update(Path(__file__).resolve().parents[1], args.check)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
