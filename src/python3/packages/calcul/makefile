include $(AIDA_HOME)/config/local_cfg.mk


install :
	echo installing package calcul in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='*.py.*' --exclude='makefile' ../calcul $(PY3_LIB_DIR)) ;
	
doc : 
	 
clean :

depend :
