include $(AIDA_HOME)/config/local_cfg.mk

install :
	@echo operators documentation generation in $(PY3_LIB_DIR)/aito/resources/;
	./do_doc.sh $(shell python3 -c 'import os ; from AITO_operators import operators ; [ print(f"{oper}") for oper in operators.keys() ]')

	@echo installing package aito in $(PY3_LIB_DIR);
	rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='*.pyc' --exclude='makefile' --exclude='src_manual' ../aito $(PY3_LIB_DIR) ;

	@echo installing aito in $(AIDA_HOME)/bin
	$(INSTALL) aito_main.py $(AIDA_HOME)/bin/aito ;

	@echo operators documentation local remove
	rm ./resources/*.html ;

clean :
	
depend :
	
