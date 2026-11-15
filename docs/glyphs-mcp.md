# Driving Glyphs through Glyphs MCP

Practical notes from real sessions. Versions move, so check before relying on a quirk:
these were seen with Glyphs MCP 2.7.0 and Glyphs 4.1.

## Reading

- `read_entities` gives glyph metadata, layer widths and bounds, paths, kerning, feature
  blocks. It has no anchors and no component positions.
- When the document has no unsaved changes, the saved `.glyphs` file is the same data and
  can be read with the tools here. Spot-check against live bounds, because positions of
  automatically aligned components can be stale in the file.
- Glyphs' own glyph database (default anchors, composite recipes, categories) is
  `GlyphData.xml` inside the application bundle.

## Editing

- Typed jobs need a saved file with no unsaved changes. Scripts run on anything.
- After duplicating a font and saving the copy, close it and open it again from disk.
  Typed jobs fail with a target conflict on a copy that was never reopened.
- The plain job calls (`start_job`, `get_job`, `apply_job`, `accept_job`) answer far more
  briefly than the edit-workflow calls. Use them for typed jobs. Scripts have to go
  through `start_edit_workflow`.
- A script checks every expected old value before its first write, and prints a readback
  at the end. It never saves or closes a font.
- `kerning_edit` refuses pairs whose group has no members. Removing dead pairs takes a
  script, and the designer's explicit yes.
- After a save, Glyphs sometimes marks the document as changed again although nothing
  differs. Saving again gives the same file. Changing the text in an Edit tab also counts
  as a change.

## Verifying

- Read the changed glyphs back from Glyphs.
- Run `./tybota diff` on the saved file against the snapshot from before the step.
- For outlines, compare bounds and node counts, and check direction and extremes again.

## Known gaps

- `path_diagnostics` has failed with an internal error. `./tybota audit` covers the same
  ground from the saved file.
