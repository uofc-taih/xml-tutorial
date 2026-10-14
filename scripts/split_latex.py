#!/usr/bin/env python3
"""Split Quarto's single combined book .tex into per-chapter fragment files.

Quarto always renders a book to one monolithic .tex. That is painful to
collaborate on, so this script splits it into a multi-file project that mirrors
the book's source layout:

    <out>/main.tex                 preamble + \\begin{document} + frontmatter
                                   + \\part{...} dividers + \\input{...} per chapter
    <out>/chapters/<src>.tex       one fragment per source .qmd (no preamble)
    <out>/figures/                 left untouched, next to main.tex

The mapping is positional: Quarto emits exactly one top-level
\\chapter / \\chapter* per book chapter file, in the same order the chapters
appear in _quarto.yml. We extract that order from _quarto.yml (the only .qmd
tokens in it are the chapter entries) and pair it 1:1 with the chapter
boundaries in the .tex. If the counts ever disagree we fail loudly rather than
silently misalign the files.

Usage:
    split_latex.py <quarto_yml> <latex_dir>

<latex_dir> must contain exactly one .tex (the combined book, not yet split).
That file is replaced by main.tex + chapters/.
"""

import os
import posixpath
import re
import sys

QMD_RE = re.compile(r'([^\s"\']+\.qmd)')
# A top-level sectioning boundary line: \chapter, \chapter*, \part, \part*
BOUNDARY_RE = re.compile(r'^\\(chapter|part)\*?[\[{]')
CHAPTER_RE = re.compile(r'^\\chapter\*?[\[{]')
# \includegraphics[opts]{path} on a single line.
GRAPHICS_RE = re.compile(r'(\\includegraphics(?:\[[^\]]*\])?\{)([^}]*)(\})')


def normalize_graphics(line):
    """Collapse '../' segments in \\includegraphics paths.

    Quarto writes figure paths relative to the PROJECT ROOT via the source
    chapter dir, e.g. '1-basics/../figures/x.png' or
    'index_files/mediabag/2-xlm/../figures/xlm/y.pdf'. Once content is \\input
    from main.tex those paths resolve against main.tex's dir, and the leading
    'chapter-dir/..' would require empty stub dirs to exist. Collapsing them to
    'figures/x.png' / 'index_files/mediabag/figures/xlm/y.pdf' means the bundle
    only needs the real asset folders next to main.tex.
    """
    return GRAPHICS_RE.sub(
        lambda m: m.group(1) + posixpath.normpath(m.group(2)) + m.group(3),
        line,
    )


def chapter_order(quarto_yml):
    """Ordered list of chapter .qmd paths, as they appear in _quarto.yml."""
    paths = []
    with open(quarto_yml, encoding="utf-8") as fh:
        for line in fh:
            # Skip comment lines so a commented-out chapter is not picked up.
            if line.lstrip().startswith("#"):
                continue
            paths.extend(QMD_RE.findall(line))
    if not paths:
        sys.exit(f"error: no .qmd chapters found in {quarto_yml}")
    return paths


def find_tex(latex_dir):
    """The single combined .tex in latex_dir (ignoring an existing main.tex)."""
    found = [
        f for f in os.listdir(latex_dir)
        if f.endswith(".tex") and f != "main.tex"
    ]
    if len(found) != 1:
        sys.exit(
            f"error: expected exactly one combined .tex in {latex_dir}, "
            f"found {found}"
        )
    return os.path.join(latex_dir, found[0])


def segment(body_lines):
    """Split body into ('front'|'part'|'chapter', [lines]) segments in order."""
    segments = []
    cur_type, cur = "front", []
    for line in body_lines:
        if BOUNDARY_RE.match(line):
            segments.append((cur_type, cur))
            cur_type = "chapter" if CHAPTER_RE.match(line) else "part"
            cur = [line]
        else:
            cur.append(line)
    segments.append((cur_type, cur))
    return segments


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: split_latex.py <quarto_yml> <latex_dir>")
    quarto_yml, latex_dir = sys.argv[1], sys.argv[2]

    order = chapter_order(quarto_yml)
    tex_path = find_tex(latex_dir)

    with open(tex_path, encoding="utf-8") as fh:
        lines = fh.readlines()

    try:
        begin = next(i for i, l in enumerate(lines)
                     if l.startswith(r"\begin{document}"))
        end = next(i for i, l in enumerate(lines)
                   if l.startswith(r"\end{document}"))
    except StopIteration:
        sys.exit("error: could not locate \\begin{document}/\\end{document}")

    preamble = lines[:begin + 1]          # through \begin{document}
    body = [normalize_graphics(l) for l in lines[begin + 1:end]]

    segments = segment(body)

    chapters_dir = os.path.join(latex_dir, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)

    main_body = []
    idx = 0
    for typ, seg_lines in segments:
        if typ in ("front", "part"):
            # Frontmatter (\maketitle, TOC) and \part dividers stay inline.
            main_body.extend(seg_lines)
            continue

        # typ == "chapter": pair with the next source file, positionally.
        if idx >= len(order):
            sys.exit(
                f"error: more chapters in {tex_path} than .qmd files in "
                f"{quarto_yml} ({len(order)}). Heading structure drifted."
            )
        rel = order[idx].rsplit(".qmd", 1)[0] + ".tex"   # e.g. 2-xlm/method-A.tex
        idx += 1

        frag_path = os.path.join(chapters_dir, rel)
        os.makedirs(os.path.dirname(frag_path), exist_ok=True)
        with open(frag_path, "w", encoding="utf-8") as out:
            out.writelines(seg_lines)

        # \input adds .tex itself; forward slashes are correct for LaTeX.
        main_body.append("\\input{chapters/%s}\n" % rel[:-4].replace(os.sep, "/"))

    if idx != len(order):
        sys.exit(
            f"error: fewer chapters in {tex_path} ({idx}) than .qmd files in "
            f"{quarto_yml} ({len(order)}). Heading structure drifted."
        )

    main_path = os.path.join(latex_dir, "main.tex")
    with open(main_path, "w", encoding="utf-8") as out:
        out.writelines(preamble)
        out.writelines(main_body)
        out.write("\\end{document}\n")

    os.remove(tex_path)  # drop the monolith; main.tex + chapters/ replace it

    print(f"split {os.path.basename(tex_path)} -> main.tex + {idx} fragments "
          f"under {chapters_dir}")


if __name__ == "__main__":
    main()
