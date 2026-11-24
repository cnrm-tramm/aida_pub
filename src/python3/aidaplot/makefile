include $(AIDA_HOME)/config/local_cfg.mk

#PYTHON_X_Y		= $(shell python3 -c 'import sys; print ("python%d.%d" % (sys.version_info[0], sys.version_info[1]))')
#PY_LIB_DIR		= $(AIDA_HOME)/lib/$(PYTHON_X_Y)


COMMANDS_PY= \
	adp \
	adpbatch

IMPORTS_PY= \
	adp_tracer.py

PICS=Bitmaps/*
FONDFILE=Cartes/*
DOCFILE=Doc/*.pdf

COMPILED_FILES=$(COMMANDS_PY:.py=.pyc)


all::

install: 

	@for SCRIPT in $(COMMANDS_PY); do \
	  $(INSTALL) $$SCRIPT.py $(AIDA_HOME)/bin/$$SCRIPT; \
	done

	@for SCRIPT in $(IMPORTS_PY); do \
	  $(INSTALL) $$SCRIPT $(PY3_LIB_DIR); \
	done

	@if [ ! -d $(AIDA_HOME)/share/aidaplot ]; \
        then ( $(MKDIRHIER) $(AIDA_HOME)/share/aidaplot); fi

	@if [ ! -d $(AIDA_HOME)/share/aidaplot/Bitmaps ]; \
        then ( $(MKDIRHIER) $(AIDA_HOME)/share/aidaplot/Bitmaps); fi

	@for PIC in $(PICS); do \
	    $(INSTALL) $$PIC  $(AIDA_HOME)/share/aidaplot/Bitmaps; \
	done

	@for DOC in $(DOCFILE); do \
	    $(INSTALL) $$DOC  $(AIDA_HOME)/share/aidaplot; \
	done

clean:

	@for SCRIPT in $(COMMANDS_PY); do \
	  rm -f $(AIDA_HOME)/bin/$$SCRIPT;  \
	done

	@for SCRIPT in $(IMPORTS_PY); do \
	  rm -f $(AIDA_HOME)/bin/$$SCRIPT;  \
	  rm -f $(AIDA_HOME)/bin/adp_tracer.pyc;  \
	  rm -f $(PY3_LIB_DIR)/$$SCRIPT;  \
	done

	@rm -f $(AIDA_HOME)/share/aidaplot/Bitmaps/*
	@rm -rf $(AIDA_HOME)/share/aidaplot

	@echo "nettoyage effectué..."

depend:

	@echo $(PICS)
