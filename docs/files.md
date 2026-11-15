# Files and naming

## Layout of a typeface folder

```
fonts/<name>/
  notes.md        facts, decisions, open questions
  sources/        the designer's files; never edited by Claude
  work/           working copies that Claude edits
  snapshots/      copies taken before each design pass
  proofs/         before/after images and audit reports
  exports/        test builds
```

`fonts/_template` is the empty skeleton. Everything else under `fonts/` is ignored by Git,
because this repository is public.

## Names

| File | Pattern | Example |
|---|---|---|
| Working copy | `<source name>_work.glyphs` | `Family-Regular_work.glyphs` |
| Snapshot | `<date>_<step>.glyphs` | `2026-11-15_before-brackets.glyphs` |
| Proof | `<date>_<step>.png` | `2026-11-15_brackets.png` |
| Audit report | `<date>_audit.md` | `2026-11-14_audit.md` |
| Test export | `<Family>-<Style>-test<N>.otf` | `Family-Regular-test3.otf` |

Dates are `YYYY-MM-DD`. Steps are short and lowercase with hyphens.

## Family name of the working copy

Give the working copy its own family name, for example `<Family> Work`, so a test export
installs next to the released family instead of replacing it. Set it back before merging.

## Saving

- The original in `sources/` is read-only for Claude.
- The working copy is saved only after a step has been verified, and only with the
  designer's permission for that copy.
- A snapshot is taken before every design pass, so any letter can be put back exactly.
- Glyphs may leave an `(Autosaved)` file next to a working copy. It is Glyphs' own safety
  copy. Leave it alone.

## What goes into Git

Standards, templates, tools and documentation. Not font sources, not exports, not proofs
of an unreleased typeface, not local paths. If a private repository is used later, the
ignore rules in `.gitignore` can be relaxed there.
