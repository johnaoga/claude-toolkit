---
name: new-course
description: Use when the user asks to create, add, rebrand, or scaffold a course from a Notion export in the course-rebranding workspace — e.g. "create a new course from _notion_xxx", "rebrand this course", "add gl-yyy from the notion export", or names a `_notion_<slug>` folder. Turns raw course material into a Sphinx/GitHub-Pages course repo matching the pythonr gold-standard structure used by pythonr, gl-dm, gl-aql, gl-sdlc, gl-mmds.
argument-hint: <_notion_slug folder or course slug> [target repo name]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, WebFetch, TaskCreate, TaskUpdate]
---

# New Course

## Scope

This skill is written for John Aoga's `rebranding` workspace
(`~/devlab/COURSES/rebranding/`), where the sibling course repos (`pythonr`,
`gl-dm`, `gl-aql`, `gl-sdlc`, `gl-mmds`, …) and `ADD_A_COURSE_GUIDE.md` live.
If it's invoked somewhere else, say so and ask whether the user wants the
same process adapted to a different workspace, rather than silently assuming
paths that don't exist here.

Turns unstructured course material (usually a Notion export folder) into a
new course repo, following the exact same process and structure already used
for `pythonr` (gold standard), `gl-dm`, `gl-aql`, `gl-sdlc`, and `gl-mmds`.

**The full, authoritative process lives in `ADD_A_COURSE_GUIDE.md` at the root
of the `rebranding` workspace. Read it in full before doing anything else — it
is longer and more detailed than this file, which is only a dispatcher.** This
SKILL.md exists so the workflow can be invoked directly (`/new-course
_notion_xxx`) instead of re-explaining the process each time; it does not
replace the guide.

## Arguments

`$ARGUMENTS` is the source folder (typically `_notion_<slug>`, relative to the
`rebranding/` root) and, optionally, the target repo name if it differs from
the obvious slug (e.g. `gl-xxx`).

- If the given folder doesn't exist, run `ls` on the `rebranding/` root, list
  the `_notion_*` folders you find, and ask the user which one they meant (or
  whether they're providing content another way — see "Flexible sources"
  below) instead of guessing.
- If no target repo name is given, propose one from the slug (dropping the
  `_notion_` prefix, e.g. `_notion_xxx` → `gl-xxx`) and confirm it fits the
  existing naming convention (`gl-<code>` for IFRI/PIGIER courses, or a bare
  name like `pythonr` if that's clearly the pattern here) before creating
  anything.

## Flexible sources

A course doesn't have to come from a Notion export. Per §1 of the guide,
handle whatever the user actually gives you: a Notion export folder, Google
Docs/Sheets (read via Claude-in-Chrome — tables need screenshotting, they
don't come through the text layer), a book/PDF (read its table of contents
first), or general CS knowledge for standard topics. Ask the user if it's
unclear which sources apply.

## The workflow (do not skip steps or reorder them)

This mirrors John's stated methodology and is a hard gate, not a suggestion:

1. **Draw & map.** Read the source folder/material, the current repo (if one
   already exists for this slug), 1–2 sibling repos as structural reference,
   and an existing `*.blueprint.md` as a template. Produce
   `rebranding/<repo>.blueprint.md` — course identity & audience, objectives,
   current vs. target structure, a source → chapter mapping table, evaluation,
   available images, open questions, and a build plan.
2. **Refine.** Ask the decision-shaping questions with `AskUserQuestion` for
   structured choices (structure style, whether to add the QCM, multi-entity
   or not, whether/when to create a Classroom) and free text for things like
   grading weights or class names. Update the blueprint with the answers.
   **Then stop and wait for the user to review/edit the blueprint and say
   GO.** Do not scaffold or write any course content before that.
3. **On GO — build.** Scaffold the repo per the guide's §3–§5 conventions
   (`docs/source/{conf.py,index.rst,intro,partN,part6}`, continuous chapter
   numbering, QCM system if requested, collapsible-correction exercises if
   requested). Copy `_static/quiz.*` and `scripts/generate_quizzes.py` from a
   sibling repo if adding the QCM. Build **offline to zero content warnings**
   (see the guide §6 for the exact proxy-blocking build command and the list
   of warnings that are/aren't acceptable). Branch as `rebrand/<slug>`, commit
   with the co-author trailer, push, and open a PR against `main` — **never
   push straight to `main`, never merge without the user's explicit
   go-ahead** (merging publishes to GitHub Pages).
4. **After the user approves the rendered PR** (not before): if they want a
   Google Classroom entry, create it via Claude-in-Chrome following §8 of the
   guide exactly — in particular, never tick the "not a school with students"
   attestation yourself (it's the user's factual declaration to make), and
   screenshot-verify every step of the racy topic-creation UI before trusting
   it registered.

## Guardrails (repeat back to yourself before each step)

- Never write course content or restructure the repo before the user says GO.
- Never push to `main`, never merge a PR yourself.
- Never tick Classroom's school attestation on the user's behalf.
- Zero content warnings on the offline Sphinx build is the actual bar, not "it
  built" — check the warning list per the guide, not just the exit code.
- French content, matching the source; keep the CC-BY-SA licence block and
  contact section from the existing intro template.

## When done

Update the project memory (`courses-rebranding-project.md` if present) with
what was built, the PR link/state, and any Classroom details — following the
same level of detail as the entries already there for gl-dm/gl-aql/gl-sdlc/
gl-mmds/guide-redaction, so a future session has accurate context.
