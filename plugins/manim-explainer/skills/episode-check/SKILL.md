---
name: episode-check
description: Validate an episode of John's Manim algorithm-explainer series without a microphone — headless render with the voice recorder stubbed out, contact sheets of every scene to inspect visually, a runtime estimate against the 8-minute budget, and a check that the code's narration matches the scenario word for word. Use whenever the user asks to check, test, validate, render, preview, or debug a `*_recorder_independent.py` episode ("does episode 9 still render?", "vérifie l'épisode LSH", "is the layout OK in scene 4?", "how long will this video run?", "did I break anything by editing the scenario?"), after any edit to an episode or its scenario, and always as the last step of `episode-code`.
argument-hint: <episode .py | topic | episode number>
allowed-tools: [Read, Edit, Bash, Glob, Grep]
---

# Episode check

## Scope

For episodes in John Aoga's `manim-videos` repo
(`~/devlab/COURSES/manim-videos/`): one `VoiceoverScene` subclass per file,
narration through `RecorderService`, scenario in `scenarios/NN_<topic>.md`.

Rendering an episode normally blocks on the microphone at every narration
block. The scripts in `scripts/` (in this skill's base directory) replace the
recorder with a dummy so the whole thing runs unattended. Recording itself is
John's job — never try to run the real recorder.

## 1. Environment (once)

```bash
PY=$(bash <this skill>/scripts/ensure_venv.sh)
```

Creates `~/.cache/manim-explainer/venv` on first use (Python 3.12 or 3.11 via
pyenv — newer Pythons lack Manim wheels) and prints its interpreter path; later
calls return immediately. System `ffmpeg` is required, and `latex` + `dvisvgm`
for episodes that use `MathTex`.

## 2. Narration matches the scenario

```bash
python3 <this skill>/scripts/check_narration.py <topic>_recorder_independent.py scenarios/NN_<topic>.md
```

John reads the on-screen prompt while recording, so each `voiceover(text=…)`
must appear verbatim in the scenario's **Narration** quotes. The script prints
`file:line` and the first diverging sentence for each mismatch, and the share
of the scenario's narration that the code covers (below ~90% means a paragraph
or scene was dropped). `note -` lines about spelled-out numbers are hints, not
failures.

When they differ, the **scenario is the reference** unless John says he
changed his mind in the code — ask if it's unclear which side is newer (compare
file modification times), then fix the other side.

## 3. Headless render

```bash
python3 -m py_compile <topic>_recorder_independent.py
$PY <this skill>/scripts/headless_render.py <topic>_recorder_independent.py
```

Options: `--class Name` if the file has several scenes, `--out DIR` (default
`/tmp/manim-explainer-check/<module>/`), `--wpm 150`, `--budget 480`.

It takes a minute or more for a full episode (low quality, 10 fps). Success
prints `RENDER_OK`; otherwise read the traceback — the innermost frame inside
a `sceneK_*` method is where to look. A log line `Missing packages …
RecorderService` is benign.

Then it prints:

- **Runtime estimate** per scene: narration time from the word count
  (150 words/min), animation time, and their per-block maximum, summed against
  the budget. A scene flagged *animation outlasts narration* will leave John
  silent on screen — shorten `run_time`s or split the block. Over budget →
  point at optional scenes in the scenario rather than trimming the worked
  example.
- **Stills and contact sheets**: one still each time a narration block's
  visuals are fully built, tiled 12 per sheet with a yellow `number scene`
  label.

## 4. Look at the pictures

Read every `sheet_NN.png` it lists (and individual files in `stills/` at full
size when something looks off). A render that succeeds says nothing about
layout, so this step is the actual check. Look for:

- objects or text off-screen, clipped at the frame edge, or overlapping;
- text too small to read at thumbnail size (it will be hard on a phone too);
- wrong or indistinguishable colours, highlights hidden behind fills;
- a scene with no still at all, or whose still doesn't show what the
  scenario's **Visuel** describes;
- English text on screen (everything visible should be French).

Fix, re-render, look again. For one stubborn scene, temporarily comment out the
other `self.sceneK…()` calls in `construct` to iterate faster — and restore
them before finishing.

## 5. Report

State plainly: narration check result, `RENDER_OK` or the error, estimated
runtime versus budget, what you saw on the sheets and what you fixed, and
anything you could not verify. If asked only to check, describe problems and
proposed fixes before changing narration; layout and crash fixes can go ahead.
