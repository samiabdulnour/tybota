# Standards

What an audit checks. A finding is a **defect** when there is one right answer, and a
**judgment call** when the designer has to look. Say which.

## Coverage

- The target languages are complete: every letter, in both cases, with the right accent
  form. For Czech that is á č ď é ě í ň ó ř š ť ú ů ý ž and the capitals, with the
  vertical caron on ď ť (and ľ Ľ) and the regular caron on Ď Ť.
- Printable ASCII is complete, including the backtick.
- Typographic punctuation for the languages: „ “ ‚ ‘ ’ » « › ‹ – — … and the
  non-breaking space (U+00A0).
- No glyph that should have outlines is empty. No two glyphs share a code point.
- Composites follow the standard recipe (base plus mark). A composite that contains only
  its base letter is a defect.

## Vertical metrics and overshoots

- Flat edges sit exactly on baseline, x-height, cap height, ascender and descender.
- Round edges overshoot by one value per case, top and bottom.
- Pointed and flat vertices follow one rule across the alphabet (A, V, W, M, v, w).
- The metrics in Font Info match what is drawn. An ascender value that no letter reaches
  is a judgment call to raise with the designer.
- Descender depths agree across g, j, p, q, y.

## Stems

- One vertical stem weight per case, one thin stroke weight, one serif thickness.
- Round strokes are heavier than straight ones by a consistent amount.
- Report strays of 2 units or more, grouped by value.
- The stem values in Font Info match the drawing. They matter for hinting.

## Anchors and marks

- Every base letter with accented forms has `top` and `bottom`; letters that take an
  ogonek have `ogonek`; letters that take the vertical caron have `topright`.
- Every mark has the matching `_top`, `_bottom`, `_ogonek`, `_topright`.
- Where a mark was placed by hand, the anchor should agree with the placement, so
  automatic alignment gives the same result.
- A dotless letter and its dotted form are the same drawing. Build one from the other.

## Spacing

- Sidebearings come from a small number of groups: straight, round, diagonal.
- Metrics keys are in sync with what they point at.
- A composite has the width of its base letter.
- Mirrored pairs mirror: parentheses, brackets, guillemets, slashes, arrows.
- Figures and math signs each share one logic for width.
- Flag negative sidebearings and anything far outside its group.

## Kerning

- Accented letters carry the kerning groups of their base letter. A letter whose side is
  changed by the accent (vertical caron) keeps its own group on that side.
- No pair points at a group without members or at a missing glyph.
- No group mixes shapes that kern differently.

## Paths

- Outer paths counter-clockwise, counters clockwise.
- No open paths, no stray points, no duplicate nodes.
- Nodes at the extremes of every curve.
- Coordinates are whole numbers.
- No lines that are 1 to 3 units off horizontal or vertical by accident.
- Smooth nodes are smooth: handles in line.

## Font level

- Features are generated and compile without errors.
- Ligatures and alternates are named once and reachable through a feature.
- Instances that cannot be built from the masters are removed or disabled.
- Leftover alternates and empty helper glyphs are either used or flagged.
