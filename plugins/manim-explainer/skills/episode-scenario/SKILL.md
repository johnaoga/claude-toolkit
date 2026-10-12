---
name: episode-scenario
description: Write the scenario (script) for a new animated algorithm-explainer episode in John's Manim video series — a `scenarios/NN_<topic>.md` file with the book-grounded worked example, scene breakdown, runtime budget, and full French narration. Use whenever the user wants to start, plan, script, storyboard, or outline a new episode or video on an algorithm or concept ("new episode on Bloom filters", "prépare le scénario pour CURE", "next video: FP-Growth", "let's do an explainer on A*"), or revise an existing scenario — even if they just name a topic and say "video" or "épisode". This is always the first step; it does not produce Manim code (that is `episode-code`).
argument-hint: <algorithm or topic> [book section / source]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Episode scenario

## Scope

Written for John Aoga's `manim-videos` repo (`~/devlab/COURSES/manim-videos/`):
a series of ~8-minute, example-driven animated explainers built with Manim +
manim-voiceover, mostly following *Mining of Massive Datasets* (`data/mmds.pdf`).
Each episode teaches ONE algorithm through one concrete worked example. John
records his own voice over the finished animation, reading the narration aloud.

An episode is made in two stages, with a human gate between them:

1. **Scenario** (this skill) → `scenarios/NN_<topic>.md`
2. John edits the scenario by hand until he is happy.
3. **Code** (`episode-code` skill) → `<topic>_recorder_independent.py`, only once
   John says so explicitly.

Stop after the scenario. The narration is John's voice and the scenario is where
he shapes it; code written before he has edited it gets thrown away, and he has
to re-read every line he will later record.

If the repo has an `AUTHORING_GUIDE.md` or `CLAUDE.md` with series notes (shared
datasets, newer conventions), read it — on a disagreement, the repo wins.

## Step 1 — get your bearings in the series

- `ls scenarios/` and read the **most recent scenario in full**. It is the
  best template for tone, depth, and layout, and it tells you the next episode
  number and what the previous teaser promised.
- Skim the headers/data sections of scenarios in the **same algorithm family**
  (clustering, market baskets, recommendation, link analysis, similar items,
  graphs…). You need them for continuity (Step 3).

## Step 2 — ground the example in the source

Find the algorithm's section in the book and reuse its *actual worked
example*: the dataset, the notation, the numbers, the figure references. For
MMDS, open `data/mmds.pdf` with the `pages` parameter (table of contents is
around PDF pages 7–20; never read the whole 600 pages), then read the section
itself. Other sources (Sedgewick & Wayne's *Algorithms*, a paper, John's
course notes) work the same way — ask where the file is if it isn't in `data/`.

Why this matters: a book example is already checked, viewers can find it in
the text, and fixed numbers make the animation deterministic. Compute and
verify every intermediate value you will show (run a few lines of Python
rather than doing arithmetic in your head) and record them in the scenario, so
the code stage copies numbers instead of re-deriving them.

If the book has no usable example, or the topic isn't in a book, build a small
one yourself (roughly ≤ 12 points / ≤ 8 nodes / ≤ 8 baskets — it has to stay
readable on screen) and say plainly in the scenario that it is illustrative.

## Step 3 — continuity with earlier episodes

The series rewards viewers who watched before. Look for:

- **Shared data.** Same-family episodes reuse the same dataset so numbers line
  up (the clustering episodes all use the 12 points of MMDS Fig. 7.2). Reuse it
  when the algorithm can run on it; switch only with a reason, stated on screen
  (DBSCAN switches to two moons *because* the 12 points can't show its point).
- **Callbacks.** When a number, picture, or limitation from an earlier episode
  reappears, say so in the narration ("le même objet qu'à l'épisode 2").
- **The previous teaser** — honour it in the hook if it pointed here.

## Step 4 — write `scenarios/NN_<topic>.md`

Narration and on-screen text in **French**; filenames in English.
Use this structure (headings in French, as in the existing scenarios):

```markdown
# Scénario — <Titre> : <sous-titre>

> Série « Mining of Massive Datasets » — Épisode N (suite de …)
> Cible : ≤ 8 min. Voix FR, code EN. Style identique à `kmeans_recorder_independent.py`.
> Source : <livre> §X.Y « … » (+ figures / exemples utilisés).

## Données de référence (à réutiliser dans le code)
<exact dataset, coordinates/layout suggestions, and every precomputed value
shown on screen, as tables or lists>

## Découpage des scènes (budget ~M:SS)
| # | Scène | Durée cible |
|---|-------|------|
| 0 | Jingle / titre | 0:20 |
| … | … | … |
| N | Conclusion + teaser | 0:25 |

> Total estimé : ~M:SS. <what to cut first if over>

## SCENE k — <titre de scène>
**Visuel** : <what appears, what moves, what gets highlighted — concrete enough
to implement: which objects, which colours, in what order>
**Narration** :
> <full French narration, exactly as it will be spoken>

## Hypothèses & questions ouvertes
**Hypothèses assumées :** <what was taken from the book as-is, what was chosen
by us, what is simplified or only mentioned>
**Questions ouvertes :** <numbered questions for John>
```

Typical arc, to adapt freely: jingle/title → hook that recalls the problem
(callback) → core intuition → ⭐ the worked example animated step by step (the
heart; give it the most time and mark it ⭐) → reading the result, variants,
cost and limits → key-points recap, "Merci…", teaser for the next episode.

### Narration conventions

- **Opening line**, every episode, verbatim:
  `Bonjour à tous, heureux amateurs de savoir et guerriers de l'ombre !`
- **Numbers as digits** — `238`, `3,6`, `k = 3`, `12` — not spelled out
  (`deux-cent-trente-huit`). John reads this text aloud while recording, and
  digits are faster to read at a glance. French decimal comma. Small counts in
  ordinary prose ("deux factions") are fine.
- Write for the ear: short sentences, one idea each, spoken register, the
  occasional rhetorical question. Spell letters that are read out (`B.F.S.`).
- Keep **Visuel** and **Narration** in step: each narration paragraph should
  have something happening on screen, and nothing should animate in silence
  for long. The code stage wraps one narration paragraph per voiceover block,
  so paragraph breaks are also animation beats.

### Runtime budget

Target **≤ 8 minutes**. Estimate at ~150 French words per minute and put the
per-scene durations in the table. Count the words rather than guessing — e.g.

```bash
awk '/^\*\*Narration\*\*/{n=1;next} n&&/^>/{print} n&&!/^>/&&NF{n=0}' scenarios/NN_<topic>.md | wc -w
```

(divide by 150 for minutes). If over budget, mark the weakest scenes
**(optionnelle)** in the table and heading so they are the first to cut, rather
than thinning the worked example.

## Step 5 — ask John, then hand over

Ask **2–4 questions** with `AskUserQuestion` about choices that materially
change the draft: which optional scenes to keep, runtime trade-offs, which
example or measure to lead with, which callbacks, what the teaser announces.
Ask once you have a draft, so the questions are concrete; apply the answers,
and leave anything still undecided under *Questions ouvertes*.

Then report: the file path, the estimated runtime, what is taken from the book
versus invented, and that the next step is his — edit the `.md`, then ask for
the code. Do not start the Manim file.
