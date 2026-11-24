include $(AIDA_HOME)/config/local_cfg.mk

PARTS= arbo.tex \
        format_inf.tex \
        formvec.tex \
        meta.tex 

MASTER= refman

AUXS= ${PARTS:.tex=.aux}
LOGS= ${PARTS:.tex=.log}

all : $(MASTER).pdf

install : $(MASTER).pdf
	cp $(MASTER).pdf ${AIDA_HOME}/doc

# Compilation directe tex->pdf par pdflatex.
$(MASTER).pdf : $(MASTER).tex $(PARTS)
	${AIDA_HOME}/src/doc/common/make_gitinfo.sh Vol1-reference
	$(PDFLATEX)  $(MASTER).tex
	while grep -s 'Rerun to get cross' $(MASTER).log ;\
	do $(PDFLATEX) $(MASTER).tex ;\
	done

clean :
	rm -f $(MASTER).pdf $(MASTER).aux *.log $(MASTER).toc $(MASTER).out $(AUXS) $(LOGS) *~ gitHeadLocal.gin

