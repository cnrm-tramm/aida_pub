include $(AIDA_HOME)/config/local_cfg.mk

PARTS= dev_C.tex \
       dev_gene.tex \
       dev_sh.tex \
       dev_Python.tex \
       dev_R.tex \
       install.tex \

MASTER= devguide

AUXS= ${PARTS:.tex=.aux}
LOGS= ${PARTS:.tex=.log}

all : $(MASTER).pdf

install : $(MASTER).pdf
	cp $(MASTER).pdf ${AIDA_HOME}/doc

# Compilation directe tex->pdf par pdflatex.
$(MASTER).pdf : $(MASTER).tex $(PARTS)
	${AIDA_HOME}/src/doc/common/make_gitinfo.sh Vol3-dvlpt
	$(PDFLATEX)  $(MASTER).tex
	while grep -s 'Rerun to get cross' $(MASTER).log ;\
	do $(PDFLATEX) $(MASTER).tex ;\
	done

clean :
	rm -f $(MASTER).pdf $(MASTER).aux $(MASTER).log $(MASTER).toc $(MASTER).out $(AUXS) $(LOGS) *~ gitHeadLocal.gin

