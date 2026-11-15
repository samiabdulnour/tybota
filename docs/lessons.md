# Lessons

What has worked, written down so the next session starts from it. Claude reads this file
at the start of every session and adds to it after every correction that lands.

## How a lesson gets here

1. The designer corrects something: a markup on a screenshot, a note on a glyph, a "no,
   more like this".
2. Claude makes the change, shows a proof, and the designer accepts it.
3. Claude writes the lesson below, on the same day, before moving on.

A lesson is only recorded once the result was accepted. A correction that has not landed
yet is an open question, and goes into the typeface's `notes.md` instead.

Lessons that are about one typeface only (its proportions, its quirks) go into that
typeface's `notes.md`. This file is public, so it never names an unreleased typeface.

When a lesson keeps coming up, or is clearly general, it also gets folded into
`standards.md`, `motifs.md`, `workflow.md` or `CLAUDE.md`, and the entry here says where.

## Format

```
### <date> · <area> · <short title>
- Asked: what the designer wanted or corrected.
- Tried: what did not work, if anything.
- Worked: what was accepted.
- Rule: what to do next time, in one sentence.
- Source: designer correction / designer approval / found while working.
```

Areas: terminals, serifs, curves, proportions, spacing, kerning, anchors, features,
process, tooling.

## Design

### 2026-11-14 · terminals · A drop hangs on the inside of the stroke
- Asked: drops on a, c, r in the manner of Clarendon.
- Tried: a small circle joined to the end of the arc, with the outer edge of the arc
  curving down to meet the top of the circle. It read as a wavy flag with a dot on it.
- Worked: leave the outer edge of the stroke exactly as it was and let the ball bulge on
  the inner side, meeting the inner edge in a concave corner.
- Rule: never bend the outer contour to reach a ball; grow the ball inward from it.
- Source: designer approval of the pilot.

### 2026-11-14 · serifs · A vertical serif needs a thin arc before it
- Asked: serifs on C and G where Clarendon has them.
- Tried: a narrow tooth on the end of the arc (read as a taper), then a squared outer
  shoulder with a hanging bar (read as a lid).
- Worked: keep the round outer shoulder, thin the arc to the thin-stroke weight, and let
  it run into a terminal about 0.9 of the stem wide with a flat foot.
- Rule: the serif shows through contrast between a thin arc and a heavy terminal, not
  through a separate shape stuck on the end.
- Source: designer approval of the pilot.

### 2026-11-14 · curves · A curled leg keeps its weight until the baseline
- Asked: the curled finish on the leg of R and the tail of t.
- Tried: a leg that tapered evenly from the bowl to the tip. It read as a thin swash.
- Worked: hold most of the stem weight down to the baseline, then a short upturned tail
  about 0.6 of the stem thick, cut vertically.
- Rule: taper late and short.
- Source: designer approval of the pilot.

### 2026-11-15 · serifs · Brackets belong to serifs, not to crossbars
- Asked: bracketed serifs, strong.
- Tried: rounding every inner corner between a stem and a horizontal of serif thickness.
  That also rounded the crossbars of f and t.
- Worked: bracket only where the stem ends at the serif (head) or stands on it (foot);
  a horizontal whose top edge does not run over the stem is a crossbar and stays square.
- Rule: tell a serif from a crossbar by whether the stem continues past it.
- Source: designer chose the strength; the crossbar rule was found while working.

### 2026-11-15 · terminals · New terminals keep the old extremes
- Asked: roll the motifs out without disturbing the spacing.
- Worked: place each ball and serif so the far edge sits where the old terminal ended.
  Widths, sidebearings and metrics keys stayed untouched in all but one glyph.
- Rule: change the shape inside the old bounding box first; widen only when the motif
  cannot fit, and then keep the sidebearing, not the width.
- Source: found while working, confirmed on the saved file.

## Process

### 2026-11-14 · process · Pilot, proof, then rollout
- Asked: a new design direction across the alphabet.
- Worked: draw the few letters the designer named, show before and after in one image,
  and roll out only after a yes.
- Rule: no alphabet-wide design change without an approved pilot.
- Source: designer approval.

### 2026-11-14 · process · When two drawings disagree, ask which one is right
- Asked: make a letter and its dotless form match.
- Worked: put the measurements of both side by side and let the designer pick. Then keep
  the spacing that other glyphs are keyed to, and say that this was Claude's choice.
- Rule: bring numbers, ask one question, and flag every choice made on the designer's
  behalf.
- Source: designer decision.

### 2026-11-14 · process · Diff the saved file after every step
- Worked: comparing the saved copy against the snapshot showed side effects nobody asked
  for, such as Glyphs rewriting two composites on save, and the Edit tab text counting as
  a change.
- Rule: a step is done when the diff lists the intended glyphs and nothing else.
- Source: found while working.

## Tooling

### 2026-11-14 · tooling · Render proofs from the outlines themselves
- Worked: a small rasteriser that sets text in the font's own outlines made it possible
  to look at every draft before it went into Glyphs. Three of the four motifs needed more
  than one draft.
- Rule: look at a render before writing an outline into the font. Never judge a curve by
  its coordinates.
- Source: found while working.

### 2026-11-14 · tooling · Reopen a fresh copy before typed jobs
- Worked: typed Glyphs MCP jobs failed on a duplicate that had only been saved. Closing
  it and opening it from disk fixed that.
- Rule: duplicate, save, close, reopen, then edit. Now in `glyphs-mcp.md`.
- Source: found while working.
