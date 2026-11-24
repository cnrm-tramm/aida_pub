include $(AIDA_HOME)/config/local_cfg.mk


install : doc_package
	echo installing package readers in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='*.pyc' --exclude='makefile' ../readers $(PY3_LIB_DIR)) ;

doc : doc_package doc_install

doc_package :
	# génère la doc à l'intérieur du package
	@echo generating doc for package readers; \
	rm -rf doc/build; \
	rm -f doc/index.html; \
	(cd doc && make html) ; \
	(cd doc && ln -s build/html/index.html index.html) \
	 || case "$(MFLAGS)" in *k*) fail=yes;; *) fail=no;; esac; \

doc_install :
	# installe la doc sous PY3_LIB_DIR
	@echo installing doc for package readers in $(PY3_LIB_DIR); \
	(rsync -r --delete --delete-excluded --links --exclude='*/.*' --exclude='*~' --exclude='*.pyc' --exclude='makefile' doc/build $(PY3_LIB_DIR)/readers/doc) ; \
	# on refait le lien
	rm -f $(PY3_LIB_DIR)/readers/doc/index.html; \
	(cd $(PY3_LIB_DIR)/readers/doc && ln -s build/html/index.html index.html) \

clean :
	@echo clean doc; \
	rm -rf doc/build; \
	rm -f doc/index.html; \

depend :
