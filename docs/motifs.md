# Design motifs

Recipes that have been drawn and approved before, written so they can be repeated on
another typeface. Numbers are for 1000 units per em with a vertical stem near 100, a thin
stroke near 60 and a slab serif near 52. Scale them with the stem.

Every recipe is a starting draft. The designer adjusts by eye.

## Ball terminal ("drop")

For a, c, f, j, r, y, the ear of g, J, the question mark and the figures 2, 3, 5.

- The ball is a circle with a radius of about 0.62 to 0.64 of the stem. Use about 0.56
  on tails and 0.50 on small parts such as the ear of g.
- It hangs on the inner side of the stroke. The outer edge of the stroke stays as it was
  and runs straight into the ball, so the outside of the letter does not change.
- The inner edge of the stroke meets the ball in a concave corner. The neck there is
  about half the stem.
- The ball has nodes at its extremes. The far side of the ball sits where the old
  terminal ended, so the sidebearing stays.

## Vertical serif on round terminals

For C, G, S and s.

- Thin the arc toward the terminal until it has the thin-stroke weight.
- Let it run into a vertical terminal about 0.9 of the stem wide, with a flat foot.
- The inner edge turns from the arc into the vertical with a short curve.
- On S and s, both terminals get it, mirrored through the centre of the letter.

## Curled leg and tail

For R and t.

- R: replace the straight leg and its slab with a curved leg that keeps most of the stem
  weight, touches the baseline with a small overshoot, and ends in an upturned tail cut
  vertically. The tail is about 0.6 of the stem thick at the end.
- t: let the tail curve further up and end in a cut across the stroke.
- K and k keep straight legs, as in Clarendon.

## Bracketed serifs

For every head and foot serif on a vertical stem.

- Replace the inner corner with a curve that climbs the stem and reaches along the serif.
- Light: 36 up, 28 along. Strong: 64 up, 46 along.
- Shorten the reach on short serifs so at least 14 units of flat serif remain.
- Leave crossbars (f, t) and the vertical serifs of arms (E, F, L, T, Z) square unless
  asked.
- `./tybota brackets` previews this on any font. Diagonal strokes need their own pass.

## How to apply a motif

1. Snapshot the working copy.
2. Pilot on the letters the designer named.
3. Render a before/after proof and wait for a yes.
4. Roll out to the rest, proof again.
5. Re-check sidebearings and kerning where an edge moved.
