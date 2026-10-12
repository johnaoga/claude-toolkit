---
name: episode-code
description: Generate the Manim + manim-voiceover Python file for an episode of John's algorithm-explainer video series from its approved scenario (`scenarios/NN_<topic>.md` → `<topic>_recorder_independent.py`), then validate it with a headless render. Use whenever the user asks to generate, write, implement, or animate the code for an episode ("generate the code for episode 14", "le scénario est prêt, fais le manim", "code the Bloom filter video"), to add, rework, or fix scenes in an existing `*_recorder_independent.py`, or to re-sync an episode after the scenario's narration changed. Requires an existing scenario — if there is none, use `episode-scenario` first.
argument-hint: <episode number | scenario path | topic>
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Episode code

## Scope

Second stage of an episode in John Aoga's `manim-videos` repo
(`~/devlab/COURSES/manim-videos/`). The first stage (`episode-scenario`)
produced `scenarios/NN_<topic>.md`, which John then edited by hand. This skill
turns that scenario into one Manim file at the repo root and proves it renders.

John records his voice afterwards: the code uses `RecorderService`, which shows
him each narration block and waits for him to speak it. So the file must run
start to finish unattended *except* for the microphone, and the text it shows
him must be exactly what he approved.

If no scenario exists for the topic, or John hasn't said it is ready, say so
and stop — the scenario is where the narration gets decided. If the repo has an
`AUTHORING_GUIDE.md` or `CLAUDE.md`, read it; on a disagreement the repo wins.

## Step 1 — read before writing

1. The **scenario, in full**. Re-read it from disk even if you wrote it: John
   edits it between stages.
2. **One or two existing episodes closest in visual vocabulary** — they are the
   style reference and a source of working helpers to copy:

   | Need | Look at |
   |---|---|
   | 2D points, clusters, centroids | `kmeans_`, `hclust_`, `dbscan_recorder_independent.py` |
   | Dendrograms, heatmap matrices | `hclust_recorder_independent.py` |
   | Curves / line charts | `elbow_recorder_independent.py` |
   | Graphs: nodes, edges, flows | `pagerank_`, `simrank_`, `girvan_newman_…` |
   | Grids / tables / matrices of cells | `svd_`, `itemcf_`, `minhash_`, `lsh_…` |
   | Item chips, icons, lattices | `apriori_recorder_independent.py` |
   | Text / character boxes | `shingles_`, `distances_recorder_independent.py` |

   `Glob` for `*_recorder_independent.py` — the list grows with the series.
   Read the helpers and two or three scenes, not the whole 1000 lines.

## Step 2 — write `<topic>_recorder_independent.py`

Code, identifiers, and comments in English; every string that appears on
screen or is spoken, in French.

```python
from manim_voiceover.services.recorder import RecorderService
from manim_voiceover import VoiceoverScene
from manim import *  # noqa: F403
import numpy as np

np.random.seed(1234)


class <Topic>VideoRecorderIndependent(VoiceoverScene):
    # Reference data from the scenario's "Données de référence" (book section, figure).
    POINTS = {...}

    def construct(self):
        recorder = RecorderService()
        recorder._whisper_model = None  # Disable transcription
        self.set_speech_service(recorder)

        # Compute anything data-driven once, so every scene draws the same numbers.
        self.precomputed = self._compute()

        self.scene0_jingle();      self.clear()
        self.scene1_hook();        self.clear()
        # ... one method per scenario scene ...
        self.sceneN_conclusion()

    # ---- helpers ----
    def accentText(self, text, **kwargs):
        return Text(text, font="Georgia", **kwargs)

    def _fmt(self, v):  # French decimal comma for on-screen numbers
        iv = int(round(v))
        return str(iv) if abs(v - iv) < 1e-9 else str(v).replace(".", ",")

    # ---- scenes ----
    def scene0_jingle(self):
        with self.voiceover(text="""[Click Record and say:]
        Bonjour à tous, heureux amateurs de savoir et guerriers de l'ombre !
        ...""") as tracker:
            title = Text("<Titre>", font_size=64)
            self.play(Write(title), run_time=2)
            self.wait(max(0, tracker.duration - 2))
            self.play(FadeOut(title))
```

### The rules that make an episode recordable

- **One class** named `<Topic>VideoRecorderIndependent`, **one `sceneK_<name>`
  method per scenario scene**, called in order from `construct` with
  `self.clear()` between them. A scene marked optional in the scenario stays a
  separate method so it can be dropped by deleting one line.
- **Every animation lives inside a voiceover block**, one block per narration
  paragraph (split a long scene into several blocks at the scenario's paragraph
  breaks — each is one take at the microphone):

  ```python
  with self.voiceover(text="""[Click Record and say:]
  <narration paragraph>""") as tracker:
      self.play(..., run_time=1.5)
      self.play(..., run_time=1.0)
      self.wait(max(0, tracker.duration - 2.5))   # 2.5 = animation time above
  ```

  `tracker.duration` is the length of John's recording. Give each `play` an
  explicit `run_time`, subtract their sum, and wait out the rest so the picture
  finishes with the sentence. The `max(0, …)` guard matters: a short take would
  otherwise ask for a negative wait.
- **Narration is copied verbatim from the scenario** — same words, same
  punctuation, digits as digits. John reads the prompt on screen while
  recording; a paraphrase means he records words he never approved. If a line
  seems wrong or unspeakable, change the scenario and tell him, don't quietly
  diverge. Keep narration as plain string literals (no f-strings) so it can be
  checked mechanically.
- **Numbers on screen come from class data or the one precomputation**, and
  match the scenario's reference tables. Never re-roll random data per scene.
- Pace animations to the narration: for a paragraph of *w* words the take lasts
  about *w* / 2.5 seconds. Animations that run much longer than that leave John
  silent on screen; much shorter leaves a static frame — add a highlight or
  build the picture in more steps.

### Manim gotchas learned on this series

- **Place data through an `Axes`.** Data lives in its own coordinates (x up to
  12, say); the frame is about 14 × 8 centred on the origin. Build an `Axes`
  and position everything with `axes.c2p(x, y)` — including graph nodes, where
  the axes are only a coordinate mapper and never drawn. Hand-computed screen
  positions are the main source of off-screen objects.
- **Scenes are self-contained.** `self.clear()` wipes mobjects between scenes,
  so each scene rebuilds its axes and objects. Plain attributes on `self`
  survive: use them for precomputed data, not for live mobjects.
- **`MathTex`/`Tex` need LaTeX and are slow.** Use `Text`/`accentText` for
  labels and plain numbers; keep `MathTex` for real formulas. Inside f-strings
  double the braces (`{{…}}`).
- **Big numeric matrices are unreadable.** Show an N×N matrix as a heatmap of
  `Square`s coloured with `interpolate_color`; show digits only up to about 3×3,
  or zoom on the cells being discussed.
- **Text sizes**: titles 40–64, body 24–32, labels in dense figures no lower
  than about 16. Check long French labels against the frame width.
- **One palette** for groups: `[BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, …]`;
  `YELLOW` for the thing being pointed at, greys for inactive elements.
- **`set_z_index`** nodes and markers above edges and regions, or highlights
  disappear behind fills.
- **`self.wait(0)` raises** in Manim ≥ 0.19. Real recordings never hit it; the
  headless check handles it. Don't "fix" it by removing the `max(0, …)` idiom.

## Step 3 — validate (required before saying it's done)

Follow the `episode-check` skill: its scripts live in the sibling directory
`../episode-check/scripts/` relative to this skill's base directory.

```bash
PY=$(bash <episode-check>/scripts/ensure_venv.sh)
python3 -m py_compile <topic>_recorder_independent.py
python3 <episode-check>/scripts/check_narration.py <topic>_recorder_independent.py scenarios/NN_<topic>.md
$PY <episode-check>/scripts/headless_render.py <topic>_recorder_independent.py
```

Fix until the narration check reports 0 problems and the render prints
`RENDER_OK`. Then **read every contact sheet it lists** and fix what you see:
objects off-screen or clipped, overlapping text, unreadable sizes, wrong
colours, a scene that never shows its key picture. Re-render after fixes. A
clean render with a broken layout is the usual failure, and only looking finds
it.

## Step 4 — report

Tell John, briefly:

- the file and class name, and the estimated runtime from the render (flag
  scenes to cut if it is over 8 minutes);
- how to record: `manim -pql <topic>_recorder_independent.py <Topic>VideoRecorderIndependent`
  (`-pqh` for the final render);
- anything illustrative or faked on screen versus computed from the book's
  data, and any place the scenario was changed or could not be followed.
