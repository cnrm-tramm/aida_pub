# This directory's subdirectories are not fully independent; 
# --> If you start "from scratch" you have to build them in 
#  a certain order.
# --> If you just updated one, you can also cd into it and run `make' 
#  without going through this Makefile.

include $(AIDA_HOME)/config/local_cfg.mk

default: all

# attention, l'ordre des sous-repertoire est important.
## SB : ajout d'un test pour lancement sur makefile specifique : make USE_MAKEFILE=makefile_francazal clean depend install

SUBDIRS = gene rapt oper

all-recursive clean-recursive install-recursive depend-recursive check-recursive :
	@if [ -d $(AIDA_HOME)/lib ]; then set +x; \
        else (set -x; $(MKDIRHIER) $(AIDA_HOME)/lib); fi

	#dummy_to_make_bash_happy previent un SUBDIRS vide
	for subdir in $(SUBDIRS) $$dummy_to_make_bash_happy; do            \
	  target=`echo $@ | sed s/-recursive//`; \
	  if [ -n "$(USE_MAKEFILE)" -a -f $$subdir/$(USE_MAKEFILE) ]; then \
	    echo making $$target in $$subdir;     \
	    (cd $$subdir && $(MAKE) -f $(USE_MAKEFILE) USE_MAKEFILE=$(USE_MAKEFILE) $$target)     \
	     || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	  else \
	    echo making $$target in $$subdir;     \
	    (cd $$subdir && $(MAKE) $$target)     \
	     || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	   fi ; \
	done && test -z "$$fail"

all: all-recursive

depend: depend-recursive

clean: clean-recursive

install: install-recursive

