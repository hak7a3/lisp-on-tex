.PHONY: test clean

TMPDIR=/tmp
STYLEFILES=$(wildcard ./*.sty)
EXAMPLE_SOURCE=$(wildcard examples/*.tex)
OUTER_EXAMPLE_SOURCE=$(wildcard outer-examples/*.tex)
EXAMPLE= $(subst examples/repl.pdf,,$(EXAMPLE_SOURCE:.tex=.pdf))
TUG2013= ./tug2013/slide.pdf
TARGETS= LICENSE README $(STYLEFILES) $(EXAMPLE) $(EXAMPLE_SOURCE) $(TUG2013)

lisp-on-tex.zip: $(TARGETS) 
	if [ -d $(TMPDIR)/lisp-on-tex ]; then rm -rf $(TMPDIR)/lisp-on-tex; fi
	if [ -e $(TMPDIR)/lisp-on-tex.zip ]; then rm $(TMPDIR)/lisp-on-tex.zip; fi
	mkdir $(TMPDIR)/lisp-on-tex
	cp --parents $^ $(TMPDIR)/lisp-on-tex/
	cd $(TMPDIR); zip -r $@ ./lisp-on-tex
	cp $(TMPDIR)/$@ .

$(subst examples/showfont.pdf,,$(EXAMPLE)): %.pdf: %.tex
	cd examples && TEXINPUTS='../;' pdflatex $(notdir $<)

examples/showfont.pdf: %pdf: %tex
	cd examples && echo 'cmr10' | TEXINPUTS='../;' xelatex $(notdir $<)

outer-examples/facterutaso.pdf: %.pdf: %.tex
	cd outer-examples && TEXINPUTS='../;' uplatex $(notdir $<)
	cd outer-examples && dvipdfmx $(notdir $(<:.tex=.dvi))

outer-examples/facterutaso_nogc.pdf: %.pdf: %.tex
	cd outer-examples && TEXINPUTS='../;' uplatex $(notdir $<)
	cd outer-examples && dvipdfmx $(notdir $(<:.tex=.dvi))

test: $(wildcard test/test-*.tex)
	cd test && for target in $(notdir $^); do \
      TEXINPUTS='../;' $(PYTHON) jenkins-qstest.py $$target; done

clean:
	rm -f test/*.xml test/*.lgout $(EXAMPLE)
