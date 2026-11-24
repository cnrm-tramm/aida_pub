# This directory's subdirectories are mostly independent; you can cd
# into them and run `make' without going through this Makefile.

## COMPILATION RECURSIVE DE AIDA
##  - la variable SUBDIRS contient la liste des sous-répertoires à compiler
##  - 2) on peut lancer make sur des fichiers spécifiques :
##          ex : make USE_MAKEFILE=makefile_XXX clean depend install
##      Les fichiers makefile_XXX seront alors pris comme fichier d'entrée de
##      make.
##      Ce système a été utilisé par SAFIRE pendant une longue période de
##      problème avec la compilation des librairies LAPACK et BLAS. ATTENTION,
##      maintenir dans le répertoire 2 versions de makefile (le "vrai"
##      makefile et le makefie_XXX) est une opération lourde et douloureuse...

# inclure le fichier $(AIDA_HOME)/config/local_cfg.mk *s'il existe*
-include $(AIDA_HOME)/config/local_cfg.mk

stop_error =	echo " " ; \
				echo "    ****** origine du local_cfg.mk : " `head -2 $(AIDA_HOME)/config/local_cfg.mk | cut -c2-` ; \
				echo " " ; \
				exit 1

# la compilation de la doc est faite manuellement
SUBDIRS = lib script python3 doc/sphinx

default: all


all-recursive clean-recursive depend-recursive install-recursive: $(AIDA_HOME)/config/local_cfg.mk
	# 2 explications : 
	#   1) dummy_to_make_bash_happy previent un SUBDIRS vide
	#   2) Dans les makefiles, il est difficile de faire le test :
	# si AIDA_LIB est défini, je l'utilise, sinon je prends $AIDA_HOME/lib
	# Donc, on le fait ici, en shell, avant tous les makefiles "fils", et il
	# faut que le même shell se poursuive ensuite. ( ";\" après le "fi" )
	@if test -z "$$AIDA_LIB"; then        \
	  export AIDA_LIB=$$AIDA_HOME/lib ;   \
	fi ;\
	for subdir in $(SUBDIRS) $$dummy_to_make_bash_happy; do            \
	  target=`echo $@ | sed s/-recursive//`; \
	  if [ -n "$(USE_MAKEFILE)" -a -f $$subdir/$(USE_MAKEFILE) ]; then \
	    echo making $$target in $$subdir;     \
	    (cd $$subdir && $(MAKE) -f $(USE_MAKEFILE) USE_MAKEFILE=$(USE_MAKEFILE) $$target)     \
	     || case "$(MFLAGS)" in *k*) fail=yes;; *) $(call stop_error);; esac; \
	  else \
	    echo making $$target in $$subdir;     \
	    (cd $$subdir && $(MAKE) $$target)     \
	     || case "$(MFLAGS)" in *k*) fail=yes;; *) $(call stop_error);; esac; \
	  fi ; \
    done && test -z "$$fail";
	@if [ -n "$(USE_32BIT_TOO)" ] ; then 													\
		target=`echo $@ | sed s/-recursive//`;												\
		echo making -f $(USE_32BIT_TOO) $$target in $(pwd);									\
		($(MAKE) -f $(USE_32BIT_TOO) $$target)    											\
		|| case "$(MFLAGS)" in *k*) fail=yes;; *) $(call stop_error);; esac;				\
	fi ;
	@echo "    **** c'est fini **** " ;

check_HOME:
	@if test -z "$$AIDA_HOME"; then            \
	  echo '$$AIDA_HOME' pas defini !!!  ;     \
	  exit -1 ;  \
	fi

check_py_package:
	./script/installateur/check_AIDA_PY_dependencies.sh
	@if test -f ./script/installateur/AIDA_manager.sh ; then \
		cp ./script/installateur/AIDA_manager.sh $(AIDA_HOME)/bin/ ; \
	fi

$(AIDA_HOME)/config/local_cfg.mk: check_HOME
	./script/set_make_config.sh

checks: check_HOME $(AIDA_HOME)/config/local_cfg.mk
	

all: checks all-recursive

clean: checks clean-recursive

depend: checks depend-recursive

#install: checks install-recursive
install: checks install-recursive check_py_package

