#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1
/* le _XOPEN_SOURCE_EXTENDED  est la pour voir strdup */

#include  <stdlib.h>
#include  <string.h>

#include <gene.h>

#include "ErRapt.h"

#ifndef AIDA_HOME
#define AIDA_HOME "/users/mmmamnp/mma/aida"
#endif

#define	OK	0
#define	SYSERR	-1
#define	NO_AIDA	+1
#define	NO_SPECIF	+2
#define	NO_HOME	+3
#define	INUTIL	+4
#define	NOM_EXT_LEN	25

char *
GetEnvMsg (const int num)
{
  switch (num)
    {
    case OK:
      return "";
    case NO_AIDA:
      return "The name of the envir. variable doesn't start with AIDA_";
    case NO_SPECIF:
      return "Envir. variable not defined, using $AIDA_HOME + ext";
    case INUTIL:
      return "Envir. variable defined exactly as $AIDA_HOME + ext";
    case NO_HOME:
      return
	"Envir. variable AIDA_HOME not defined, using compile-time default";
    default:
      return NULL;
    }
}

/**
 *   Cette fonction fait un simple getenv (3C) mais si
 * l'appel echoue, elle renvoie une valeur par defaut
 * selon les regles de l'environnement AIDA.
 *
 *    Contrairement a getenv, cette fonction alloue de
 * l'espace memoire pour son resultat. Donc :
 *    - Cet espace est definitivement disponible pour
 *      le programme appelant.
 *    - C'est au programme appelant de faire un "free"
 *      des qu'il n'a plus besoin de la chaine.
 *
 * \return
 *     0 : OK
 *    -1 : Erreur "systeme", voir Errapt
 *    +1 : Le nom recherche n'est pas de la forme "AIDA_*"
 *    +2 : Var non trouvee, on retourne $AIDA_HOME+(ext.)
 *    +3 : Var et $AIDA_HOME non trouvee, on retourne la
 *         valeur codee en dur a la compilation.
 *    +4 : OK, var trouvee, mais inutile car égale à $AIDA_HOME+(ext.)
 */
int
AidaGetEnv (const char *Nom, char **resu_str)
{
  char *EnvStr;
  int CodRet = OK;
  char NomExt[NOM_EXT_LEN];
  char *default_val;

  if (Nom == NULL)
    {
      *resu_str = NULL;
      errapt = RAPT_EINVAL;
      return SYSERR;
    }

  if (strncmp (Nom, "AIDA_", 5) != 0)
    {
      *resu_str = NULL;
      return NO_AIDA;
    }

  /* NomExt = la partie après AIDA, en minuscule */
  strncpy (NomExt, &Nom[5], NOM_EXT_LEN - 1);
  NomExt[NOM_EXT_LEN - 1] = 0;
  ConvMin (NomExt);
  if (!strcmp (NomExt, "home"))
    strcpy (NomExt, "");

  EnvStr = getenv (Nom);
  if (EnvStr == NULL)
    {
      EnvStr = getenv ("AIDA_HOME");
      if (EnvStr == NULL)
	{
	  CodRet = NO_HOME;
	  EnvStr = AIDA_HOME;
	}
      else
	{
	  CodRet = NO_SPECIF;
	}
      *resu_str = strconcat3 (EnvStr, "/", NomExt);
      if (*resu_str == NULL)
	{
	  errapt = RAPT_ENOMEM;
	  return SYSERR;
	}
    }
  else
    {
      CodRet = OK;
      *resu_str = strdup (EnvStr);
      if (*resu_str == NULL)
	{
	  errapt = RAPT_ENOMEM;
	  return SYSERR;
	}
      /* Code erreur spécifique si AIDA_xxx == AIDA_HOME/xxx  */
      EnvStr = getenv ("AIDA_HOME");
      if (EnvStr != NULL)
	{
	  default_val = strconcat3 (EnvStr, "/", NomExt);
	  if (default_val != NULL)
	    {
	      if (!strcmp (*resu_str, default_val))
		CodRet = INUTIL;
	      free (default_val);
	    }
	}
    }
  return CodRet;
}
