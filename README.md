# claude-toolkit

Personal collection of [Claude Code](https://claude.com/claude-code) skills/plugins for John Aoga's teaching workflow (course rebranding at IFRI/UAC & PIGIER, mémoire writing guidelines). This repo is a local **plugin marketplace** — new tools get added here as new plugins over time.

## Plugins

| Plugin | What it does |
|---|---|
| [`course-toolkit`](plugins/course-toolkit/) | `/new-course` — scaffold a new course repo from a Notion export, following the [`rebranding`](https://github.com/johnaoga) workspace's Sphinx/GitHub-Pages conventions. `/thesis-checker` — check a mémoire/thesis PDF against the writing guidelines and produce a compliance report. |

## Using it

In Claude Code, register this repo as a marketplace and install a plugin from it:

```
/plugin marketplace add johnaoga/claude-toolkit
/plugin install course-toolkit@johnaoga-claude-toolkit
```

Both skills currently assume they're running inside the `rebranding` workspace
(`~/devlab/COURSES/rebranding/`) — see each skill's "Scope" note.

## Adding a new plugin

1. `mkdir -p plugins/<name>/.claude-plugin plugins/<name>/skills/<skill-name>`
2. Add `plugins/<name>/.claude-plugin/plugin.json` (`name`, `description`, `author`).
3. Add `plugins/<name>/skills/<skill-name>/SKILL.md` (frontmatter: `name`, `description`, `argument-hint`, `allowed-tools`).
4. Register the plugin in `.claude-plugin/marketplace.json`.
