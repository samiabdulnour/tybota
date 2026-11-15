# Tybota

A working kit for developing typefaces in Glyphs with Claude as the production assistant.
It holds the standards a font is checked against, the file conventions, the templates,
and a small set of Python tools that read a `.glyphs` file directly.

The designer draws and decides. Claude audits, fixes the mechanical things, drafts
design passes when asked, and proofs every change before it is kept.

## What is in here

| Path | What it is |
|---|---|
| `CLAUDE.md` | The rules Claude follows in this project. Read this first. |
| `docs/workflow.md` | The phases of a font project, from first audit to export. |
| `docs/standards.md` | What "consistent" means: coverage, metrics, anchors, spacing, kerning, paths, features. |
| `docs/files.md` | Where files live and how they are named. |
| `docs/glyphs-mcp.md` | Practical notes on driving Glyphs through Glyphs MCP. |
| `docs/motifs.md` | Reusable design recipes: ball terminals, vertical serifs, curled tails, bracketed serifs. |
| `docs/lessons.md` | What has worked. Grows with every correction that lands. |
| `tools/` | The `tybota` command and its Python package. |
| `templates/` | Audit report, per-font notes, session log, proof texts. |
| `fonts/` | One folder per typeface. Local only: sources are not committed. |

## Quick start

The tools need Python 3.9 or newer and nothing else.

```bash
./tybota audit path/to/Font.glyphs
```

```bash
./tybota proof path/to/Font.glyphs --text "Příliš žluťoučký kůň" --out proof.png
```

```bash
./tybota diff before.glyphs after.glyphs
```

```bash
./tybota brackets path/to/Font.glyphs --rise 64 --run 46 --out brackets.png
```

`audit` prints a Markdown report. `proof` renders text with the font's own outlines.
`diff` lists which glyphs changed between two saves. `brackets` previews bracketed serifs
without touching the font. All four only read files.

## Starting a new typeface

1. Copy `fonts/_template` to `fonts/<name>`.
2. Put the working source in `fonts/<name>/sources`.
3. Fill in `fonts/<name>/notes.md`.
4. Ask Claude for a read-only audit. It follows `docs/workflow.md`.

## Privacy

This repository is public. Font sources, exports and per-font folders are ignored by Git
on purpose. Nothing about an unreleased typeface goes into a commit unless the designer
says so.
