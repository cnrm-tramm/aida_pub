include $(AIDA_HOME)/config/local_cfg.mk

###############################################################################
# - toutes les doc sont compilées
# - les nouvelles documentations doivent être référencées dans :
#                   CATALOG_OPER.tex 
###############################################################################

MASTER = CATALOG_OPER

all :  $(MASTER).pdf

install : $(MASTER).pdf
	cp $(MASTER).pdf ${AIDA_HOME}/doc

# Pour ce que j'en comprends, il faut faire plusieurs passes de pdflatex ets
# makeindex pour obtenir un document dont les références de pages sont
# correctes.
$(MASTER).pdf : *.tex arguments/*.tex formules/*.tex
	# récupération d'info git
	${AIDA_HOME}/src/doc/common/make_gitinfo.sh oper 
	# première passe
	$(PDFLATEX)  $(MASTER).tex
	# génération des index
	$(MAKEINDEX) $(MASTER).idx
	# prise en compte des index dans le pdf
	$(PDFLATEX)  $(MASTER).tex
	# mise à jour des index
	$(MAKEINDEX) $(MASTER).idx
	# prise en compte des index à jour dans le pdf
	$(PDFLATEX)  $(MASTER).tex

clean :
	rm -f $(MASTER).pdf *.aux *.log *.bbl *.toc *.ilg *.ind *.idx *.out gitHeadLocal.gin

