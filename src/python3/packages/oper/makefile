include $(AIDA_HOME)/config/local_cfg.mk


install :
	echo installing package oper in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='*.py.*' --exclude='makefile' ../oper $(PY3_LIB_DIR)) ;
	$(AIDA_HOME)/bin/oper_py_2doc.py -n
	
doc : 
	$(AIDA_HOME)/bin/oper_py_2doc.py
	 
clean :

depend :
