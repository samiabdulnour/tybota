"""Command line: audit, proof, diff, brackets. Every command only reads font files."""
import argparse
import sys

from . import audit, brackets, diff, raster
from .font import Font


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tybota", description="Read-only tools for Glyphs source files.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("audit", help="print a Markdown audit report")
    p.add_argument("font")
    p.add_argument("--languages", default="english,czech", help="comma-separated, see tools/tybota/charsets.py")
    p.add_argument("--out", help="write the report to this file instead of printing it")

    p = sub.add_parser("proof", help="render text in the font's outlines to a PNG")
    p.add_argument("font")
    p.add_argument("--text", action="append", required=True, help="one line of text; repeat for more lines; /name picks a glyph by name")
    p.add_argument("--against", help="an earlier save: each line is shown before (above) and after (below)")
    p.add_argument("--out", default="proof.png")
    p.add_argument("--scale", type=float, default=0.15, help="pixels per font unit")

    p = sub.add_parser("diff", help="list the glyphs that changed between two saves")
    p.add_argument("before")
    p.add_argument("after")

    p = sub.add_parser("brackets", help="preview bracketed serifs without touching the font")
    p.add_argument("font")
    p.add_argument("--rise", type=float, default=64, help="how far the curve climbs the stem")
    p.add_argument("--run", type=float, default=46, help="how far the curve reaches along the serif")
    p.add_argument("--text", action="append", help="lines to show; default is a short sample")
    p.add_argument("--out", default="brackets.png")
    p.add_argument("--scale", type=float, default=0.2)

    args = ap.parse_args(argv)

    if args.cmd == "audit":
        text = audit.Audit(args.font, tuple(x.strip().lower() for x in args.languages.split(",") if x.strip())).report()
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("Report written to", args.out)
        else:
            print(text)

    elif args.cmd == "proof":
        after = Font(args.font)
        before = Font(args.against) if args.against else None
        rows, skipped = [], set()
        for line in args.text:
            for f in ([before] if before else []) + [after]:
                names, missing = raster.glyph_names(f, line)
                skipped.update(missing)
                rows.append([(f, n) for n in names])
        size = raster.proof(rows, args.out, scale=args.scale)
        print(f"Proof written to {args.out} ({size[0]} x {size[1]})")
        if skipped:
            print("Not in the font, left out:", " ".join(sorted(skipped)))

    elif args.cmd == "diff":
        print(diff.diff(args.before, args.after))

    elif args.cmd == "brackets":
        plain, soft = Font(args.font), Font(args.font)
        done = brackets.bracketed(soft, args.rise, args.run)
        rows = []
        for line in args.text or ["HEnildpu", "Hamburgefonstiv"]:
            for f in (plain, soft):
                names, _ = raster.glyph_names(f, line)
                rows.append([(f, n) for n in names])
        raster.proof(rows, args.out, scale=args.scale)
        print(f"{sum(done.values())} corners in {len(done)} glyphs would be bracketed. Preview written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
