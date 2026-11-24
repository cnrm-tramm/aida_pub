# Génération automatique
# Ne pas modifer manuellement
#


.SECONDEXPANSION:

ifndef AIDA_LIB
AIDA_LIB = $(AIDA_HOME)/lib
endif

# La variable doit exister
# Elle ne sera utilisée que si nautilus existe sur la machine
export NAUTILUS_SCRIPTS_DIR=$(HOME)/.local/share/nautilus/scripts

# -------------------------------------
# Variables de compilations spécifiques
# -------------------------------------
# "WITHOUT_LAPACK" par défaut, car plus passe-partout.
# WITHOUT_LAPACK=FALSE
WITHOUT_LAPACK=TRUE

# -------------------------------------
# Variables de compilations générales
# -------------------------------------
# Environnement d'exécution de l'appli AIDA
export LD_RUN_PATH=$(AIDA_LIB)

C_ANSI                   = gcc -ansi
C_99                     = gcc -std=c99
CC                       = $(C_ANSI)
C_STRICT_FLAGS           = -pedantic-errors -Wall
C_OPT_FLAGS              = -O
C_PROF_INFO_FLAGS        = -p
C_COV_INFO_FLAGS         = -fprofile-arcs -ftest-coverage
C_DEBUG_INFO_FLAGS       = -g
C_VERBOSE_FLAGS          = -Q
C_DEBUG_FLAGS            = $(C_DEBUG_INFO_FLAGS)
C_PIC_FLAGS              = -fpic
PICFLAGS                 = $(C_PIC_FLAGS)

LD                       = gcc
LD_RUNPATH_FLAGS         =  -L
LD_SHLIB_FLAGS           = -shared
DYN_LOADER_LIB           = -ldl


F77                      = gfortran
LIB_PATH_FORTRAN         = /usr/lib/x86_64-linux-gnu
C_FORTRAN_MIXING_LIB     = /usr/lib/x86_64-linux-gnu/libgfortran.so.5.0.0
F77_UNDERSCORE_FLAGS     = -funderscoring
F77_NO_UNDERSCORE_FLAGS  = -fno-underscoring
OPTS_FORTRAN_LAPACK      = -O $(F77_UNDERSCORE_FLAGS) $(PICFLAGS)

SPHINXBUILD              = /usr/share/sphinx/scripts/python3/sphinx-build

UDUNITS2_INC_PATH        = /usr/include
PYTHON_INC_PATH          = /usr/include/python3.10
LIB_PATH_PYTHON          = /usr/lib/x86_64-linux-gnu
PYTHON_3_Y               = $(shell python3 -c 'import sys; print ("python%d.%d" % (sys.version_info[0], sys.version_info[1]))')
PY3_LIB_DIR              = $(AIDA_HOME)/lib/$(PYTHON_3_Y)

# Sous linux, il faut créer des liens so -> so.1; s0.1 -> sl
EXTRA_CMD_SL             = (cd  $(AIDA_HOME)/lib; \
                           ln -sf ./lib$(STD_LIBRARY_NAME).sl lib$(STD_LIBRARY_NAME).so.1; \
                           ln -sf ./lib$(STD_LIBRARY_NAME).so.1 lib$(STD_LIBRARY_NAME).so )
# La même règle que ci-dessus, écrite pour fonctionner sur le prérequis de la cible courante.
EXTRA_CMD_SL_PREREQ      = (cd  $(AIDA_HOME)/lib; \
                           ln -sf ./$< $(<:.sl=.so.1); \
                           ln -sf ./$(<:.sl=.so.1) $(<:.sl=.so) )


#  QUEL INTERET DE PRECISER LE PATH /usr/bin ? ----
DEPEND                   = makedepend
MAKE                     = make
INSTALL                  = install
TAR                      = tar
MKDIRHIER                = mkdir -p
CEXTRACT                 = $(AIDA_HOME)/bin/cextract

LATEX                    = latex
PDFLATEX                 = pdflatex
DVIPS                    = dvips
BIBTEX                   = bibtex
HTLATEX                  = htlatex
MAKEINDEX                = makeindex

# A SUPPRIMER ?
# Certains programmes ne sont pas portables (compilables seulement sur
# certains systemes).
# On définit donc ici des "EXTRA_LIST", dont le contenu dépend du système.
# Chaque de ces liste sera ajoutée à la liste programmes portables dans
# les makefiles correspondant (EXTRA_SUBDIRS_C_LECTURE sera utilisée
# dans le makefile de src/C/lecture).
   EXTRA_SUBDIRS_C_ECRITURE =  #vec2cdf
    EXTRA_SUBDIRS_C_LECTURE =
      EXTRA_SUBDIRS_ASC2VEC =


