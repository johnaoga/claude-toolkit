#!/usr/bin/env python
"""Check that an episode's voiceover text matches its scenario verbatim.

The author reads the scenario while recording, so every `voiceover(text=...)`
string in the code must appear word for word in the scenario's narration
(the `>` quote lines under each **Narration** heading). Also notes large
numbers spelled out in French, since the series writes values as digits
(small counts like "deux factions" are normal prose and are left alone).

Needs only the standard library.

Usage:
    python check_narration.py <episode.py> <scenario.md>
"""
import ast
import re
import sys
from pathlib import Path

RECORD_PREFIX = re.compile(r"\[Click Record and say:\]", re.I)
SPELLED = re.compile(
    r"(?<!pour )\b(onze|douze|treize|quatorze|quinze|seize|"
    r"vingt|trente|quarante|cinquante|soixante|cent|cents|mille)\b", re.I)


def norm(text):
    text = RECORD_PREFIX.sub(" ", text)
    text = text.replace("\u2019", "'").replace("\u00a0", " ").replace("\u202f", " ")
    return re.sub(r"\s+", " ", text).strip()


def scenario_narration(md):
    """Concatenate the quote lines that follow each **Narration** marker."""
    out, active = [], False
    for line in md.splitlines():
        stripped = line.strip()
        if re.match(r"\*\*Narration\*\*", stripped):
            active = True
            continue
        if active:
            if stripped.startswith(">"):
                out.append(stripped.lstrip("> "))
            elif stripped and not stripped.startswith(">"):
                active = False
    return norm(" ".join(out))


def code_narration(source):
    """Yield (lineno, text | None) for each voiceover(text=...) call."""
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "voiceover"):
            value = next((k.value for k in node.keywords if k.arg == "text"), None)
            if value is None and node.args:
                value = node.args[0]
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                yield node.lineno, value.value
            else:
                yield node.lineno, None


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    code_path, md_path = Path(sys.argv[1]), Path(sys.argv[2])
    scenario = scenario_narration(md_path.read_text(encoding="utf-8"))
    if not scenario:
        sys.exit(f"No narration found in {md_path} (expected '>' lines under **Narration**).")

    problems, covered, total = 0, 0, 0
    for lineno, text in code_narration(code_path.read_text(encoding="utf-8")):
        total += 1
        if text is None:
            print(f"{code_path.name}:{lineno}: voiceover text is not a plain string - compare by hand")
            problems += 1
            continue
        spoken = norm(text)
        if spoken in scenario:
            covered += len(spoken)
        else:
            problems += 1
            # Point at the first sentence that diverges, to make the fix obvious.
            sentences = re.split(r"(?<=[.!?:;])\s+", spoken)
            bad = next((s for s in sentences if s not in scenario), spoken)
            print(f"{code_path.name}:{lineno}: not verbatim in scenario -> \"{bad[:140]}\"")
        for word in sorted({m.group(0).lower() for m in SPELLED.finditer(spoken)}):
            print(f"{code_path.name}:{lineno}: note - spelled-out number \"{word}\", should it be a digit?")

    ratio = covered / max(1, len(scenario))
    print(f"\n{total} voiceover blocks, {problems} problem(s); "
          f"code covers ~{ratio:.0%} of the scenario narration.")
    if ratio < 0.9:
        print("Scenario narration is missing from the code (a scene or paragraph was skipped?).")
    sys.exit(1 if problems or ratio < 0.9 else 0)


if __name__ == "__main__":
    main()
