---
name: thesis-checker
description: Use when the user asks to check, audit, review, or grade-check a mémoire/thesis PDF against the writing guidelines — e.g. "check this thesis PDF", "does this mémoire follow the guidelines", "review my student's PDF for compliance", "audit this memoire.pdf". Produces a structured compliance report against executive_writing_guidelines.md.
argument-hint: <path/to/memoire.pdf> [licence|master]
allowed-tools: [Read, Write, Bash, Glob, Grep, AskUserQuestion, Artifact]
---

# Thesis / Mémoire Checker

## Scope

Written for John Aoga's `rebranding` workspace
(`~/devlab/COURSES/rebranding/`), where the reference guidelines live at
`_notion_writings/executive_writing_guidelines.md` (also published chapter by
chapter at the `guide-redaction` site). If that file can't be found relative
to the current workspace, `Glob` for it before falling back to asking the
user for its path — don't invent guideline content from memory.

Checks a student's mémoire PDF against the guidelines and produces a
compliance report. This is a heuristic aid for the reviewer, not a substitute
for actually reading the thesis — say so in the report.

## Arguments

`$ARGUMENTS` is the PDF path, and optionally `licence` or `master` if the user
already knows the level (this changes which checks apply — see §1 of the
guidelines). If not given, try to detect it from the title page; if that's
ambiguous, ask with `AskUserQuestion` rather than guessing, since several
checks (état de l'art depth, discussion vs. matrice comparative, tool
justification) diverge by level.

## Step 0 — read the reference

Read `_notion_writings/executive_writing_guidelines.md` in full first. It is
the single source of truth for every check below — if this skill's checklist
and the guidelines ever disagree, the guidelines win.

## Step 1 — extract text

```bash
pdfinfo "<pdf>"                                   # page count, sanity check it's a real PDF
pdftotext -layout "<pdf>" /tmp/thesis_extract.txt # -layout preserves indentation/columns
```

`pdftotext` inserts a form-feed (`\f`) between pages, so page numbers can be
recovered: `awk 'BEGIN{RS="\f"}{print NR": "$0}' /tmp/thesis_extract.txt` gives
you page-indexed text for grepping and quoting with an accurate page number.

**Sanity-check the extraction before trusting it.** If the text per page is
near-empty or full of garbled characters (common with scanned/image-only PDFs
or unusual font encodings), say so explicitly in the report, fall back to
reading key pages directly with the `Read` tool (it reads PDFs natively,
`pages:` param, max 20 pages per call — use it surgically on the pages that
matter, not the whole document), and flag any check you couldn't verify as
"non vérifiable" rather than guessing.

## Step 2 — locate the front matter and chapter boundaries

Grep the page-indexed extract for section markers to build a page map before
doing any judgment calls: `Dédicace`, `Remerciement`, `Mots.?clés`,
`Résumé`/`Abstract`, `Sommaire`/`Table des matières`, `Introduction`
(générale, not a chapter's own), each `Chapitre N`, `Conclusion` (générale),
`Bibliographie`/`Références`. Titles vary in student documents — search
loosely (case-insensitive, accent-tolerant) and confirm against the table of
contents page(s) rather than the first regex hit.

## Step 3 — run the checks

For each item, produce a verdict (**Conforme** / **Partiel** / **Non
conforme** / **N/A**), a short quoted excerpt with its page number as
evidence, and — for anything not fully conforme — a one-line concrete fix.
Never state a page number or quote you didn't actually see in the extracted
or read text.

**1. Principes fondamentaux** — Read enough of the document end-to-end to
judge: does it read as a coherent narrative, or a fragmented assembly of
notes? Is it self-contained (could a reader outside the project follow it)?
Confirm the detected Licence/Master level matches what the front matter
claims (démonstration de maîtrise vs. contribution originale).

**2. Préliminaires**
- Dédicace ≤ 2 lines, no personal commentary/justification.
- Remerciements present (any content is fine — this one's a soft check).
- Mots-clés: exactly 5, semicolon-separated (`;`).

**3. Résumé / Abstract** — Check it reads as one fluid paragraph (not headed
subsections) and that the 5 piliers are actually present in order: Constat →
Problème → Objectif → Méthodologie → Résultats (with quantified results, not
just a description of what was built). Note if the Abstract is a real
translation or missing.

**4. Introduction & Conclusion**
- Introduction: does it restate/expand the résumé, and does the "annonce du
  plan" read as prose (❌ a mechanical "Chapitre 1: ... Chapitre 2: ..." list
  is a direct violation) rather than a bare list?
- Conclusion: reformulated in the past tense, and structured as
  rappel-problématique → synthèse-contributions → limites → perspectives (all
  four present, roughly in that order).

**5. État de l'art (Chapitre 1 equivalent)** — Are technical terms/acronyms
defined on first use? Scan for the word "faiblesse(s)" applied to prior work —
the guidelines ban it in favor of "limite(s)"; flag every occurrence with page
number. Does the chapter conclude by naming an explicit gap that motivates the
thesis's objective (not just "few tools exist")?

**6. Méthodologie (Chapitre 2 equivalent)** — Is there a tools/frameworks
table (not paragraphs of description of standard tools like Python/VS Code)?
For Master-level work, are tool choices justified (not just listed)? Is there
a global architecture diagram, a technical-design section, and formally
defined evaluation metrics with their physical interpretation (what does 0 vs
1 mean)?

**7. Résultats (Chapitre 3 equivalent)** — Is the test environment specified
(CPU/GPU/RAM, dataset size/split/class balance) before results are shown? Are
quantitative results presented before functional/UI validation? For Licence:
is there a comparative matrix table against existing solutions? For Master: is
there an actual discussion (not just a table) that engages with the état de
l'art from chapter 1, including an honest analysis of the work's own
limitations/failure cases?

**8. Charte de style** — Scan for banned "bling-bling" vocabulary: superlative
or hyperbolic adjectives without a number backing them up (e.g.
*extrêmement*, *révolutionnaire*, *très puissant*, *impressionnant*,
*flagrant(e)*, and similar unquantified claims of excellence). Quote each hit
with page number and suggest the measurable reformulation. Check heading depth
doesn't exceed 3 levels (look for numbering patterns like `2.3.1.4` in the
table of contents or headers — that's a violation).

**9. Figures, tableaux, équations, code** — Spot-check a sample of figures and
tables (not necessarily all, for a long document): is each one referenced in
the surrounding text (not just dropped in)? Are captions in French? For any
equation you find, is every variable/symbol defined immediately after it? For
any code listing, is there prose explaining what the key lines do (not just
the raw listing)?

**10. Usage de l'IA et intégrité** — This is mostly declarative/unverifiable
from the PDF text alone. Check only if there's an explicit AI-usage
declaration or acknowledgment section; if bibliography entries look
suspicious (implausible DOIs, mismatched titles/authors you can't verify),
flag them as "à vérifier" rather than asserting they're fabricated.

## Step 4 — write the report

Produce two artifacts:

1. **A saved Markdown report** next to the PDF (or in the workspace scratch
   area if the PDF's directory isn't writable), named
   `<pdf-basename>.rapport-conformite.md` — one section per guideline item
   above, in order, each with its verdict, evidence, and fix.
2. **A rendered report as an Artifact** for easier review — load the
   `artifact-design` skill first, then build a clean report page: a summary
   scorecard at the top (counts of Conforme/Partiel/Non conforme/N/A and the
   top 3 priority fixes), then the same per-section detail as the Markdown
   version with status badges. Keep it text-forward (this is a review
   document, not a dashboard) — no charts needed for a 10-item checklist.

Close both with an explicit caveat: this is an automated heuristic pass over
extracted text, it can miss layout-only issues (e.g. dédicace alignment/
centering) or misjudge nuanced writing-quality calls, and it does not replace
the supervisor actually reading the thesis.
