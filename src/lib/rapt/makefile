include $(AIDA_HOME)/config/local_cfg.mk

LOCAL_AIDA_HOME     = $(AIDA_HOME)
INST_DIR            = $(AIDA_HOME)
CFLAGS              = $(C_DEBUG_INFO_FLAGS) $(C_STRICT_FLAGS) -Wextra
SHLIBLDFLAGS        = $(LD_SHLIB_FLAGS)
INC_PATH            = -I$(AIDA_HOME)/include
ALLDEFINES          = $(INC_PATH)
LIB_PATH            = -L$(AIDA_HOME)/lib
STD_LIBRARY_NAME    = rapt
DEPEND_FILE         = $(STD_LIBRARY_NAME).depend

SRCS                = AidaGetEnv.c \
                      AidaTypNom.c \
                      ErRapt.c

OBJS_STAT           = ${SRCS:.c=.os}
OBJS_DYN            = ${SRCS:.c=.od}
HDRS                = ${SRCS:.c=.h}

.SUFFIXES : .os .od

.c.os: RaptStruct.h
	$(CC) $(CFLAGS) $(INC_PATH) -DAIDA_HOME=\"$(LOCAL_AIDA_HOME)\" -c -o $@ $<

.c.od: RaptStruct.h
	$(CC) $(CFLAGS) $(C_PIC_FLAGS) -DAIDA_HOME=\"$(LOCAL_AIDA_HOME)\" $(INC_PATH) -c -o $@ $<


$(STD_LIBRARY_NAME) : lib$(STD_LIBRARY_NAME).a lib$(STD_LIBRARY_NAME).sl $(STD_LIBRARY_NAME).h


all: $(STD_LIBRARY_NAME) 

lib$(STD_LIBRARY_NAME).sl: $(OBJS_DYN) $(AIDA_HOME)/lib/libgene.sl
	$(LD) $(LD_RUNPATH_FLAGS) $(AIDA_HOME)/lib $(LD_SHLIB_FLAGS) -o lib$(STD_LIBRARY_NAME).sl $(OBJS_DYN) -L $(AIDA_HOME)/lib -lgene -lz -lm -lc

lib$(STD_LIBRARY_NAME).a: $(OBJS_STAT)
	ar rv lib$(STD_LIBRARY_NAME).a $?


$(STD_LIBRARY_NAME).h : $(HDRS) ./RaptStruct.h
	echo "#ifndef _RAPT_INCLUDED" > $(STD_LIBRARY_NAME).h;\
	echo "#define _RAPT_INCLUDED" >>$(STD_LIBRARY_NAME).h;\
	cat ./RaptStruct.h >>$(STD_LIBRARY_NAME).h ;\
	cat $(HDRS) | grep -a -v "RaptStruct\.h" >>$(STD_LIBRARY_NAME).h ;\
	echo "#endif /* _RAPT_INCLUDED */" >>$(STD_LIBRARY_NAME).h
	cp $(STD_LIBRARY_NAME).h $(INST_DIR)/include/ ;\


install: lib$(STD_LIBRARY_NAME).a lib$(STD_LIBRARY_NAME).sl $(STD_LIBRARY_NAME).h
	cp lib$(STD_LIBRARY_NAME).a $(INST_DIR)/lib ;\
	cp lib$(STD_LIBRARY_NAME).sl $(INST_DIR)/lib ;\
	cp $(STD_LIBRARY_NAME).h $(INST_DIR)/include/ ;\
	$(EXTRA_CMD_SL)


clean:
	rm -f *.os *.od *.o *.c~ core *.a *.sl rapt.h $(DEPEND_FILE)

#  le DEPEND_FILE Il ne faut pas oublier de fabriquer rapt.h avant de calculer 
depend: $(STD_LIBRARY_NAME).h $(SRCS)
	touch $(DEPEND_FILE)
	$(DEPEND) -f $(DEPEND_FILE) -s "# Automatically generated" -Y $(ALLDEFINES) -- $(SRCS)

# If a dependency file exists, reference it
-include $(DEPEND_FILE)
