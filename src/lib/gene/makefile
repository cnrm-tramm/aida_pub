include $(AIDA_HOME)/config/local_cfg.mk

CFLAGS           = $(PICFLAGS) $(C_OPT_FLAGS) $(C_STRICT_FLAGS) -Wextra
DEPEND_FILE      = gene.depend
ALLDEFINES       = $(CFLAGS)
INST_DIR         = $(AIDA_HOME)
STD_LIBRARY_NAME = gene

SRCS=ConvMaj.c        ConvMajPrem.c  ConvMin.c  \
     eclat.c          InEnsInt.c \
     OteDebut.c       OteFin.c       chaine_vide.c  \
     strncasecmp_blankend.c        \
     add_to_static_str.c             strconcat2.c   strconcat3.c \
     strwrap.c        \
     strchrcount.c    \
     str_tab_free.c   \
     EclatLdc.c       \
     Endianness.c     Swap_Bytes.c   \
     CheckDirExist.c  file_exists.c  \
     try_add_rights.c \
     flt_cmp.c        \
     decode_date.c    decode_heure.c \
     calend.c   \
     teste_nombre_str.c


OBJS = ${SRCS:.c=.o}
HDRS = ${SRCS:.c=.h}

.c.o: gene.h
	$(CC) $(CFLAGS) -c $<


all : gene

gene : gene.h $(DEPEND_FILE) libgene.sl 

libgene.sl: gene.h $(OBJS) 
	$(LD) $(LD_SHLIB_FLAGS) -o libgene.sl $(OBJS) -lm

libgene.a: $(OBJS)
	ar rv libgene.a $?

gene.h : $(HDRS)
	echo "#ifndef _GENE_INCLUDED" > gene.h;\
	echo "#define _GENE_INCLUDED" >>gene.h;\
        cat $(HDRS) >>gene.h ;\
        echo "#endif /* _GENE_INCLUDED */" >>gene.h
	cp gene.h $(INST_DIR)/include/;\


install: libgene.sl gene.h
	@echo cp libgene.sl $(INST_DIR)/lib ;\
	cp libgene.sl $(INST_DIR)/lib ;\
	cp gene.h $(INST_DIR)/include/;\
	$(EXTRA_CMD_SL)
        
clean:
	rm -f $(OBJS) core core.*  *.sl gene.h $(DEPEND_FILE)

$(DEPEND_FILE):  $(SRCS)
	touch $(DEPEND_FILE)
	$(DEPEND) -f$(DEPEND_FILE) -s "# DO NOT DELETE" -- $(ALLDEFINES) -- $(SRCS)

#  Il ne faut pas oublier de fabriquer gene.h avant de calculer 
#  les dépendances.
depend::    gene.h $(DEPEND_FILE)

# If a dependency file exists, reference it
-include $(DEPEND_FILE)
