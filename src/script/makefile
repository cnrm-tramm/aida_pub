include $(AIDA_HOME)/config/local_cfg.mk

# On a constaté que les "install" ont tendance à enlever 
# des droits sur les fichiers installés. Pour des raisons
# pratique, on souhaite garder de la souplesse. 
# Donc, on installe avec cp
INSTALL=cp

COMMANDS=  \
	aida_env.sh


install:
	for SCRIPT in $(COMMANDS); do \
	  $(INSTALL) $$SCRIPT $(AIDA_HOME)/bin; \
	done 

clean:
	@echo "nettoyage effectué..."

depend::
