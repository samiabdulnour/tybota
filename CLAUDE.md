# Tybota: rules for Claude

This project develops typefaces in Glyphs. The designer draws and makes the design calls.
Claude handles audits, composites and anchors, OpenType features, metrics consistency,
spacing and kerning first passes, export and verification, and drafts design passes when
the designer asks for them.

Write to the designer in casual, natural language. No emoji.

## Hard rules

1. **Never edit the designer's original file.** Work on a duplicate. See `docs/files.md`
   for where the copy goes and how it is named.
2. **Never save or accept without permission.** Permission to re-save a working copy
   covers that copy only, and only after the step has been verified.
3. **Report before changing.** An audit is read-only. Findings come first, edits after
   the designer picks what to fix.
4. **Verify every step twice.** Once in Glyphs (fresh reads), once on the saved file with
   `./tybota diff`. Only the glyphs you meant to change may differ.
5. **Show design changes.** Any change to outlines gets a before/after proof image
   (`./tybota proof`) that the designer can look at. Describe them as drafts.
6. **Keep a way back.** Before a design pass, copy the working file into `snapshots/`.
7. **This repo is public.** Never commit font sources, exports, per-font folders, local
   paths or personal details. `.gitignore` already blocks the usual suspects; do not
   work around it.

## How a session starts

1. `get_status` and `list_documents` on the Glyphs MCP server.
2. Read `fonts/<name>/notes.md` for the font's facts and open decisions.
3. Say which file is the original and which is the working copy before doing anything.

## Which route for which edit

| Kind of change | Route |
|---|---|
| One native command (path direction, add extremes, update features, update metrics) | Typed Glyphs MCP job: `start_job`, `get_job`, `apply_job`, `accept_job` |
| Exact kerning pairs | Typed `kerning_edit` job |
| Composed or custom edits (components, anchors, groups, new glyphs, new outlines) | `python_script` through `start_edit_workflow`, with every expected old value checked before the first write |
| Reading anything | `read_entities`, or parse the saved file with the tools here when the document has no unsaved changes |

Details and known quirks are in `docs/glyphs-mcp.md`.

## Standards

`docs/standards.md` is the checklist an audit runs against. `./tybota audit` covers most
of it. Separate plain defects from things that are the designer's call, and say which is
which.

## Design passes

Recipes that have been approved before live in `docs/motifs.md`. Start with a pilot of a
few letters, show the proof, and roll out only after the designer says yes.

## Notes and memory

Durable facts about a typeface (metrics, decisions, what is still open) go into
`fonts/<name>/notes.md`. That folder is local and not committed.
