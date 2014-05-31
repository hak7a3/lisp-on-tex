TMPDIR=/tmp/lisp-on-tex
STYLEFILES=$(wildcard ./*.sty)
EXAMPLE=$(wildcard ./examples/*.tex) $(wildcard ./examples/*.pdf)
TUG2013=./tug2013/slide.tex ./tug2013/slide.pdf \
					$(wildcard ./tug2013/bench/*/*.tex) \
					$(wildcard ./tug2013/bench/*/*.pdf)
TARGETS= LICENSE README test.tex \
					$(STYLEFILES) $(EXAMPLE) $(TUG2013)
lisp-on-tex.zip: $(TARGETS)
	if [ -d $(TMPDIR)/lisp-on-tex ]; then rm -rf $(TMPDIR)/lisp-on-tex; fi
	if [ -e $(TMPDIR)/lisp-on-tex.zip ]; then rm $(TMPDIR)/lisp-on-tex.zip; fi
	mkdir $(TMPDIR)/lisp-on-tex
	cp --parents $^ $(TMPDIR)/lisp-on-tex/
	cd $(TMPDIR); zip -r $@ ./lisp-on-tex
	cp $(TMPDIR)/$@ .
