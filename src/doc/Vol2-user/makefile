include $(AIDA_HOME)/config/local_cfg.mk

PARTS= conventions.tex \
	   doc.tex \
       ecriture.tex \
       graphe.tex \
       lecture.tex \
	   nommage_vect.tex \
       traite.tex \
	   user.tex \
       utile.tex

MASTER= user

AUXS= ${PARTS:.tex=.aux}
LOGS= ${PARTS:.tex=.log}

all : $(MASTER).pdf

install : $(MASTER).pdf
	cp $(MASTER).pdf ${AIDA_HOME}/doc

# Compilation directe tex->pdf par pdflatex.
$(MASTER).pdf : $(MASTER).tex $(PARTS)
	${AIDA_HOME}/src/doc/common/make_gitinfo.sh Vol2-user
	$(PDFLATEX)  $(MASTER).tex
	while grep -s 'Rerun to ' $(MASTER).log ;\
	do $(PDFLATEX) $(MASTER).tex ;\
	done

# Compilation classique tex->dvi par latex.
$(MASTER).dvi : $(PARTS) $(MASTER).tex 
	$(LATEX) $(MASTER).tex
	while grep -s 'Rerun to get cross' $(MASTER).log ;\
	do $(LATEX) $(MASTER).tex ;\
	done

# transformation dvi->ps par latex.
$(MASTER).ps : $(MASTER).dvi  
	$(DVIPS) -ta4 $(MASTER).dvi -o $@


clean :
	rm -f $(MASTER).pdf $(MASTER).aux *.log $(MASTER).toc $(MASTER).out $(AUXS) $(LOGS) *~ gitHeadLocal.gin

