# This directory's subdirectories are mostly independent; you can cd
# into them and run `make' without going through this Makefile.

SUBDIRS = oper Vol1-reference Vol2-user Vol3-dvlpt premiers_pas sphinx outils

DIRS_DOCEXT = src/python3/packages/readers

default: all

doc-ext :
	for subdir in $(DIRS_DOCEXT) $$dummy_to_make_bash_happy; do            \
	  target=`echo $@ | sed s/-recursive//`; \
	  echo making doc in $$subdir;     \
	  cd $(AIDA_HOME)/$$subdir && $(MAKE) doc \
          || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"

all-recursive clean-recursive depend-recursive install-recursive: $(AIDA_HOME)/config/local_cfg.mk
	#dummy_to_make_bash_happy previent un SUBDIRS vide
	for subdir in $(SUBDIRS) $$dummy_to_make_bash_happy; do            \
	  target=`echo $@ | sed s/-recursive//`; \
	  echo making $$target in $$subdir;     \
	  (cd $$subdir && $(MAKE) $$target)     \
	   || case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"

check_HOME:
	@if test -z "$$AIDA_HOME"; then            \
	  echo '$$AIDA_HOME' pas defini !!!  ;     \
	  exit -1 ;  \
	fi

all: check_HOME all-recursive

clean: check_HOME clean-recursive

depend:

install: check_HOME doc-ext install-recursive

dist:
	for subdir in $(SUBDIRS); do                      \
	  echo making $@ of $$subdir;                     \
	  tar chof - $$subdir | gzip -c > ./$$subdir.tgz; \
	done 
