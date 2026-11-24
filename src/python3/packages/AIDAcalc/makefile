include $(AIDA_HOME)/config/local_cfg.mk


install :
	echo installing package AIDAcalc in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='makefile' --exclude='*.txt' --exclude='*.cfg' ../AIDAcalc $(PY3_LIB_DIR)) ; \
	cp AIDAcalc.py $(AIDA_HOME)/bin/adc ;\
	#cp $(AIDA_HOME)/src/lib/oper/oper_API_PY_desc.py $(PY3_LIB_DIR) ; 
	iconv -f ISO8859-15 -t UTF-8 $(AIDA_HOME)/src/lib/oper/oper_API_PY_desc.py -o $(PY3_LIB_DIR)/oper_API_PY_desc.py

	
doc : 
	 
clean :

depend :
