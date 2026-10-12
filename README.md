# claude-toolkit

Personal collection of [Claude Code](https://claude.com/claude-code) skills/plugins for John Aoga's teaching workflow (course rebranding at IFRI/UAC & PIGIER, mémoire writing guidelines, Manim explainer videos). This repo is a local **plugin marketplace** — new tools get added here as new plugins over time.

## Plugins

| Plugin | What it does |
|---|---|
| [`course-toolkit`](plugins/course-toolkit/) | `/new-course` — scaffold a new course repo from a Notion export, following the [`rebranding`](https://github.com/johnaoga) workspace's Sphinx/GitHub-Pages conventions. `/thesis-checker` — check a mémoire/thesis PDF against the writing guidelines and produce a compliance report. |
| [`manim-explainer`](plugins/manim-explainer/) | `/episode-scenario` — write the scenario (book-grounded example, scene breakdown, French narration) for a new episode of the Manim algorithm-explainer series. `/episode-code` — generate the manim-voiceover Python file from the approved scenario. `/episode-check` — headless render, contact sheets, runtime estimate, and narration-vs-scenario check. |

## Using it

In Claude Code, register this repo as a marketplace and install a plugin from it:

```
/plugin marketplace add johnaoga/claude-toolkit
/plugin install course-toolkit@johnaoga-claude-toolkit
/plugin install manim-explainer@johnaoga-claude-toolkit
```

The `course-toolkit` skills assume they're running inside the `rebranding` workspace
(`~/devlab/COURSES/rebranding/`), and the `manim-explainer` skills inside the
`manim-videos` repo (`~/devlab/COURSES/manim-videos/`) — see each skill's "Scope" note.

## Adding a new plugin

1. `mkdir -p plugins/<name>/.claude-plugin plugins/<name>/skills/<skill-name>`
2. Add `plugins/<name>/.claude-plugin/plugin.json` (`name`, `description`, `author`).
3. Add `plugins/<name>/skills/<skill-name>/SKILL.md` (frontmatter: `name`, `description`, `argument-hint`, `allowed-tools`).
4. Register the plugin in `.claude-plugin/marketplace.json`.
