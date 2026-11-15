# Workflow

Each phase ends with something the designer can look at and a decision that is theirs.

## 1. Set up

- Create `fonts/<name>/` from `fonts/_template`.
- Put the designer's source in `sources/`. It is never edited.
- Fill in `notes.md`: family name, masters, metrics, target languages, open questions.

## 2. Audit (read-only)

Run `./tybota audit` on the source and cross-check a sample of glyphs against live
readings in Glyphs. Report, in this order:

1. Coverage for the target languages, and what is missing.
2. Stems and overshoots.
3. Anchors and mark attachment.
4. Spacing: sidebearing outliers, metrics keys, mirrored pairs.
5. Kerning: groups, dead pairs.
6. Paths: direction, extremes, open paths, slips.
7. Font level: features, instances, vertical metrics, leftovers.

Use `templates/audit-report.md`. Mark each finding as a defect or a judgment call.

## 3. Mechanical fixes

Things with one right answer: path direction, broken composites, kerning groups copied
from base letters, missing glyphs with obvious recipes, generated features.

- Duplicate the font, save the copy into `work/`.
- One kind of fix per step. Verify, save the copy, move on.
- Finish with `./tybota diff` against the original and a short list of what changed.

## 4. Design decisions

Anything where two answers are defensible goes to the designer as a short question with
the measurements: which drawing is right, which stem weight, which overshoot.

## 5. Design passes

Only on request. Snapshot first, pilot on a few letters, proof, then roll out.
Recipes are in `docs/motifs.md`.

## 6. Spacing and kerning first pass

Sidebearings by group, then kerning by group. Re-check after every design pass that moved
an outline edge.

## 7. Export and test

Export a named test instance, verify tables and a few shaping samples, then hand it over
for testing in the layout application. Nothing is final until it has been seen in real text.

## 8. Merge back

When the designer is happy with the working copy, they decide whether it becomes the new
source. Record the decision and the date in `notes.md`.
