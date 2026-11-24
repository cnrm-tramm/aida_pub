include $(AIDA_HOME)/config/local_cfg.mk


install :
	echo installing package edifil in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='PourMaintenance' --exclude='*~' --exclude='makefile' ../edifil $(PY3_LIB_DIR)) ; \
	$(INSTALL) edifil_main.py $(AIDA_HOME)/bin/edifil ; 
	
doc : 
	 
clean :

depend :
