#!/bin/sh
# script for packaging...
zip -r lisp-on-tex.zip \
  ./lisp-on-tex/LICENSE \
  ./lisp-on-tex/README \
  ./lisp-on-tex/*.sty \
  ./lisp-on-tex/examples/*.tex \
  ./lisp-on-tex/examples/*.pdf \
  ./lisp-on-tex/tug2013

