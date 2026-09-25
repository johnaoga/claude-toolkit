# course-toolkit

Two skills for the IFRI/UAC & PIGIER course-rebranding and mémoire-writing workflow.

## `/new-course <_notion_slug folder> [repo-name]`

Scaffolds a new course repo from a Notion export (or other source material),
following the same 3-step process (blueprint → clarify & wait for GO → build)
already used for `pythonr`, `gl-dm`, `gl-aql`, `gl-sdlc`, and `gl-mmds`. Reads
`ADD_A_COURSE_GUIDE.md` in the `rebranding` workspace as its authoritative
process reference.

## `/thesis-checker <path/to/memoire.pdf> [licence|master]`

Checks a mémoire/thesis PDF against `_notion_writings/executive_writing_guidelines.md`
(the "Directives Exécutives de Rédaction Académique et Scientifique"), section
by section, and produces a compliance report (saved Markdown + rendered
Artifact) with verdicts, quoted evidence, and concrete fixes.

Both skills are scoped to the `rebranding` workspace — see the "Scope" note
at the top of each `SKILL.md`.
