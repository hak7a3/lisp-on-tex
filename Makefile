.PHONY: test

TMPDIR=/tmp
STYLEFILES=$(wildcard ./*.sty)
EXAMPLE_SOURCE=$(wildcard examples/*.tex)
EXAMPLE= $(EXAMPLE_SOURCE:.tex=.pdf)
TUG2013= ./tug2013/slide.pdf
TARGETS= LICENSE README $(STYLEFILES) $(EXAMPLE) $(EXAMPLE_SOURCE) $(TUG2013)

lisp-on-tex.zip: $(TARGETS) 
	if [ -d $(TMPDIR)/lisp-on-tex ]; then rm -rf $(TMPDIR)/lisp-on-tex; fi
	if [ -e $(TMPDIR)/lisp-on-tex.zip ]; then rm $(TMPDIR)/lisp-on-tex.zip; fi
	mkdir $(TMPDIR)/lisp-on-tex
	cp --parents $^ $(TMPDIR)/lisp-on-tex/
	cd $(TMPDIR); zip -r $@ ./lisp-on-tex
	cp $(TMPDIR)/$@ .

$(EXAMPLE): %.pdf: %.tex
	cd examples && TEXINPUTS='../;' pdflatex $(notdir $<)

test: $(wildcard test/test-*.tex)
	cd test && for target in $(notdir $^); do \
      TEXINPUTS='../;' $(PYTHON) jenkins-qstest.py $$target; done
