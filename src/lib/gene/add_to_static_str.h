#define	GSTR_INVARG	1
#define	GSTR_BUGARG	2
#define	GSTR_NOSPACE	3

/* On inclue ici stdlib.h, pour avoir la définition de size_t */
#include <stdlib.h>

extern int
add_to_static_str (char *s1, size_t volume_1, const char *s2);

/* On inclue ici stdio.h, pour avoir la définition de FILE */
#include <stdio.h>

extern void
raconte_GSTR_error (int error, FILE * os, char *dest, size_t taille,
		    const char *src);

extern char *
strcat_sur (char *dest, size_t taille, const char *src);

