include $(AIDA_HOME)/config/local_cfg.mk


install :
	echo installing package prod_CDF in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='makefile' --exclude='*.txt' --exclude='*.cfg' ../prod_CDF $(PY3_LIB_DIR)) ; \
	cp prod_CDF.py $(AIDA_HOME)/bin/ ;\

	
doc : 
	 
clean :

depend :
