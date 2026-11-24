include $(AIDA_HOME)/config/local_cfg.mk


COMMANDS_PY= \
	update_liste_vecteurs_vista \
	make_liste_vecteurs_vista
	
MODULES_PY=

SHELLS=

COMPILED_FILES=$(COMMANDS_PY:.py=.pyc)

#LISTE_PROFILS=$(shell ls $(AIDA_HOME)/profils)
LISTE_PROFILS=$(shell ls -F $(AIDA_HOME)/profils | grep \/$)

all::

install: clean-install
	echo installing package vista in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='*.pyc' ../vista $(PY3_LIB_DIR)) ;
	
	@$(INSTALL) main.py $(AIDA_HOME)/bin/vista
	
	@for SCRIPT in $(COMMANDS_PY); do \
	  $(INSTALL) outils/$$SCRIPT.py $(AIDA_HOME)/bin/$$SCRIPT; \
	done
	
	@for MODULE in $(MODULES_PY); do \
	  $(INSTALL) $$MODULE $(AIDA_HOME)/bin/$$MODULE; \
	done
	
	@for SHELL in $(SHELLS); do \
	  $(INSTALL) bin/$$SHELL $(AIDA_HOME)/bin/$$SHELL; \
	done

	@for PROFIL in $(LISTE_PROFILS); do \
	    if [ ! -d $(AIDA_HOME)/share/vista/vecteurs/$$PROFIL ]; \
            then ( $(MKDIRHIER) $(AIDA_HOME)/share/vista/vecteurs/$$PROFIL); fi; \
		if [ -d $(AIDA_HOME)/profils/$$PROFIL/vista/vecteurs ]; \
        	then ( cp -f $(AIDA_HOME)/profils/$$PROFIL/vista/vecteurs/*.txt $(AIDA_HOME)/share/vista/vecteurs/$$PROFIL);fi; \
	done

	@if [ ! -d $(AIDA_HOME)/share/vista/doc ]; \
        then ( $(MKDIRHIER) $(AIDA_HOME)/share/vista/doc); fi
        
	@$(INSTALL) doc/* $(AIDA_HOME)/share/vista/doc
	
	@if [ ! -d $(AIDA_HOME)/share/vista/icons ]; \
        then ( $(MKDIRHIER) $(AIDA_HOME)/share/vista/icons); fi
        
	@$(INSTALL) icons/* $(AIDA_HOME)/share/vista/icons
	
clean:
	
clean-install:

	@rm -f $(AIDA_HOME)/bin/vista
	
	@for SCRIPT in $(COMMANDS_PY); do \
	  rm -f $(AIDA_HOME)/bin/$$SCRIPT;  \
	done
	@for MODULE in $(MODULES_PY); do \
	  rm -f $(AIDA_HOME)/bin/$$MODULE;  \
	done
	@for SHELL in $(SHELLS); do \
	  rm -f $(AIDA_HOME)/bin/$$SHELL;  \
	done
	
	@rm -rf $(AIDA_HOME)/share/vista

	@echo "clean post install effectué..."

depend:
