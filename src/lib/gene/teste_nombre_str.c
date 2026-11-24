/*  Pour isblank(), qui a été officialisé dans OSIX.1-2001 et la
       norme C99 7.4.1.3.  */
#define _XOPEN_SOURCE 600

#include <ctype.h>

/** Teste si une chaine contient un nombre decimal positif sans signe
 *
 *  \return 0 si OK, ou le numéro du caractère qui 
 *  a fait échouer le test.
 *
 */
int
nombre_positif_decimal_sans_signe (const char *str)
{
  int i;
  i = 0;

/* Espaces avant */
  while (isblank (str[i]))
    i++;

/* Jusqu'a un point ou un espace, on accepte chiffres et points */
  while (str[i])
    {
      if (str[i] == '.')
	{
	  break;
	}
      if (isblank (str[i]))
	{
	  break;
	}
      if (!isdigit (str[i]))
	return i + 1;
      i++;
    }

  /* Si le caractère actuel est un point (et donc, pas un "blanc"), 
   * on accepte encore que des chiffres, jusqu'a la fin ou un blanc */
  if (str[i] == '.')
    {
      i++;
      while (str[i])
	{
	  if (isblank (str[i]))
	    {
	      break;
	    }
	  if (!isdigit (str[i]))
	    return i + 1;
	  i++;
	}
    }

/* Jusqu'a la fin, on n'accepte que des blancs */
  while (str[i])
    {
      if (!isblank (str[i]))
	return i + 1;
      i++;
    }

  return 0;
}
