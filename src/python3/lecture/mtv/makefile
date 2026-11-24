include $(AIDA_HOME)/config/local_cfg.mk


PROJ			=   mtv

COMMANDS_PY		=	mtv.py
MODULES_PY		=   temps.py
DOC_GEN			= 
DOC_DIR			= 

SHELLS			= 

all:

install:
    # TODO : on installe les modules et les exec sous $AIDA_HOME/bin
    # TODO : ce serait bien de faire de mtv un package
	@echo "installing $(PROJ) in $(AIDA_HOME)/bin"
	@for x in $(COMMANDS_PY) $(SHELLS) ; do \
		cp $$x $(AIDA_HOME)/bin/ ;  \
	done

	@for x in $(MODULES_PY) ; do \
		cp $$x $(PY3_LIB_DIR)/$$x ;  \
	done

clean:
	@echo "clean ./__pycache__"
	@find . -type d -name "__pycache__" -exec rm -rf {} \;

	@# Avec le passage à python3 temps.py est passé sous AIDA_LIB. On le supprime de $AIDA_BIN.
	@echo "clean $(AIDA_HOME)/bin"
	@for x in $(notdir $(COMMANDS_PY) $(SHELLS)) ; do \
		rm -f $(AIDA_HOME)/bin/$$x ; \
		rm -f $(AIDA_HOME)/bin/temps.py* ; \
	done

	@echo "clean $(PY3_LIB_DIR) (mtv)"
	@for x in $(MODULES_PY) ; do \
		rm -f $(PY3_LIB_DIR)/$$x ;  \
	done

depend:

