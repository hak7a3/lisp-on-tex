#!/bin/sh
# script for packaging...
TARGET="lisp-on-tex.zip"
zip $TARGET ./lisp-on-tex/LICENSE
zip $TARGET ./lisp-on-tex/README
zip $TARGET ./lisp-on-tex/*.sty
PDF_EXAMPLES="fact fpnummodule-mandelbrot rocket"
SOURCE_EXAMPLES="repl showfont"
for i in $PDF_EXAMPLES $SOURCE_EXAMPLES; do
  zip $TARGET ./lisp-on-tex/examples/$i.tex
done
for i in $PDF_EXAMPLES; do
  zip $TARGET ./lisp-on-tex/examples/$i.pdf
done
zip $TARGET ./lisp-on-tex/tug2013

