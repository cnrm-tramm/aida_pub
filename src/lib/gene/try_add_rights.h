/* Pour la definition de S_I[RWX]USR, S_I[RWX]GRP, S_I[RWX]OTH */
#include <sys/stat.h>

extern int
try_add_rights (const char *path, int mode);
