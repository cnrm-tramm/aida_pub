include $(AIDA_HOME)/config/local_cfg.mk


COMMANDS = \
	AIDA_lib/Units.py \
	doc/graph/gengraphvect.py \
   	doc/graph/ihm_config_graph_geneal_vect.py \
	doc/graph/ihm_genere_graph_geneal_vect.py \
	doc/graph/genparamvect.py \
	doc/oper_py/oper_py_2doc.py \
	graph/graph_tpr_profil_periode.py \
	lecture/histo/histo_config.py \
	lecture/mtv/mtv.py \
	processing/cree_vecteurs/creer_vect_flag_periode.py \
	processing/cree_vecteurs/recale_vecteur.py \
	processing/cree_vecteurs/creer_vect_time_sequences.py \
	ecriture/txt/prod_csv.py \
	ecriture/netcdf/prod_CDF_histo.py \
	utils/diff_acqids_list.py \
	utils/expand_acqids_list.py \
	utils/plt.py \
	utils/doy.py \
	utils/aida_env.py \
	utils/cat_vect.py \
	utils/id2datapath \
	utils/INFfiltre \
	utils/FDDfiltre \
	utils/simple_vivect.py

MODULES = \
	AIDA_lib/AIDA.py \
	AIDA_lib/AcqIdDoY.py \
	AIDA_lib/AcqId.py \
	AIDA_lib/Camp.py \
	AIDA_lib/Chrono.py \
	AIDA_lib/DataBase.py \
	AIDA_lib/fct_messages.py \
	AIDA_lib/VersionVect.py \
	AIDA_lib/AIDA_env.py \
	AIDA_lib/AIDA_mail.py \
	AIDA_lib/AIDA_logger.py \
	AIDA_lib/Units.py \
	AIDA_lib/Constantes.py \
	AIDA_lib/Misval.py \
	AIDA_lib/Fil_analyze.py \
	AIDA_lib/AIDA_name_to_CF_name.py \
	AIDA_lib/Ref_time.py \
	processing/rayonnement/corassiet.py \
	doc/graph/gengraphvect.py

PACKAGES = \
	readers \
	vista \
	calcul \
	oper \
	AIDAcalc \
	prod_CDF \
	edifil \
	aito

SUBDIRS = \
	aidaplot/ \
	lecture/mtv/

all-recursive :

install-recursive : all-recursive
	@echo "install COMMANDS in $(AIDA_HOME)/bin"
	@for SCRIPT in $(COMMANDS); do \
		$(INSTALL) $$SCRIPT $(AIDA_HOME)/bin; \
	done
	
	@mkdir -p $(PY3_LIB_DIR)
	@echo "install MODULES in $(PY3_LIB_DIR)"
	@for MODULE in $(MODULES); do \
		$(INSTALL) $$MODULE $(PY3_LIB_DIR) ; \
	done
	
	@echo "install PACKAGES"
	@cd packages; \
	for PACKAGE in $(PACKAGES); do \
		(cd $$PACKAGE && $(MAKE) install) \
		 || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"
	
	@echo "install SUBDIRS"
	@for subdir in $(SUBDIRS) $$dummy_to_make_bash_happy; do \
		echo making install in $$subdir; \
		(cd $$subdir && $(MAKE) install) \
		 || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"

clean-recursive :
	@echo "clean ./__pycache__"
	@find . -depth -type d -name "__pycache__" -exec rm -rf {} \;
	@rm -rf $(AIDA_HOME)/bin/*.py
	@rm -rf $(AIDA_HOME)/lib/python*
	
	@echo "clean in $(SUBDIRS)"
	@for subdir in $(SUBDIRS) $$dummy_to_make_bash_happy; do \
		echo making clean in $$subdir; \
		(cd $$subdir && $(MAKE) clean) \
		 || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"
	
	@echo "clean in $(PACKAGES)"
	@for PACKAGE in $(PACKAGES) ; do \
		echo making clean in $$subdir; \
		(cd packages/$$PACKAGE && $(MAKE) clean) \
		 || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"

depend-recursive :
	@echo "depend"
	@for subdir in $(SUBDIRS) $$dummy_to_make_bash_happy; do \
		echo making depend in $$subdir; \
		(cd $$subdir && $(MAKE) depend) \
		 || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"

all: all-recursive

depend: depend-recursive

clean: clean-recursive

install: install-recursive

