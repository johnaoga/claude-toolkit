# manim-explainer

Three skills for the Manim algorithm-explainer video series (`manim-videos`
repo): ~8-minute, example-driven episodes in French, built with Manim +
manim-voiceover and recorded with John's own voice. They follow the
two-stage workflow of the repo's `AUTHORING_GUIDE.md`, with a human gate in
between.

## `/episode-scenario <algorithm or topic> [book section]`

Stage 1. Grounds the worked example in the book (`data/mmds.pdf` or another
source), checks continuity with earlier episodes, and writes
`scenarios/NN_<topic>.md`: reference data, scene breakdown with a runtime
budget, per-scene visuals, and the full French narration. Asks 2–4 questions,
then stops — John edits the scenario by hand before any code is written.

## `/episode-code <episode number | scenario path | topic>`

Stage 2, once the scenario is approved. Generates
`<topic>_recorder_independent.py` (one `VoiceoverScene`, one `sceneK_*` method
per scene, narration copied verbatim into `RecorderService` voiceover blocks),
reusing helpers from the closest existing episodes, then validates it with
`episode-check` and reports how to record.

## `/episode-check <episode .py | topic>`

Validates an episode without a microphone. Bundled scripts:

| Script | What it does |
|---|---|
| `scripts/ensure_venv.sh` | Creates `~/.cache/manim-explainer/venv` once (Python 3.12/3.11 + manim) and prints its interpreter path. |
| `scripts/check_narration.py` | Checks every `voiceover(text=…)` appears verbatim in the scenario's narration, and that no scenario narration was dropped. |
| `scripts/headless_render.py` | Renders with the recorder stubbed out; prints `RENDER_OK`, a per-scene runtime estimate against the 8-minute budget, and contact sheets with one still per narration block for visual inspection. |

Requires system `ffmpeg`, plus `latex` and `dvisvgm` for episodes using `MathTex`.

All three are scoped to the `manim-videos` repo layout — see the "Scope" note
at the top of each `SKILL.md`.
