/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#define _POSIX_SOURCE

#include <ctype.h>
#include <string.h>
#include <stdlib.h>

/** Retourne "vrai" si le caractère passé en argument est un 
 * délimiteur de date valide ('/' ou '-').
 *
 * \param c : Le caractère à tester.
 */
static int
is_date_separ (int c)
{
  return ((c == '/') || (c == '-'));
}

/** Conversion en entier d'une suite de chiffres de longueur donnée.
 * Les différences avec atoi() sont :
 *   - Travaille sur un nombre de caractères donnés, et pas jusqu'au 0 final.
 *   - Pas de test que les caractères sont numériques (à faire par appelant)
 *
 * \param buf : Pointeur vers le début de la chaîne
 * \param len : Le nombre de caractères à convertir
 */
static int
a_to_int (const char *buf, int len)
{
  int res = 0;
  while (len > 0)
    {
      len--;
      res = res * 10 + (*buf - '0');
      buf++;
    }
  return res;
}

/**  Interprète une chaine de type :
 * digit/digit/[separ/]digit/digit[/separ/]digit/digit[/digit/digit]
 * sous la forme de trois entiers positifs ; jour mois année.
 *  Les séparateurs peuvent être "/" ou "-".
 *  Le "-" est implémenté car c'est le séparateur utilisé
 * dans la norme ISO-8601, mais ATTENTION : cette norme
 * recommende l'ordre AAAA MM JJ (inverse d'ici)
 *
 * Pour l'instant, pas de contrôles des bornes (du genre MM<=12)
 *
 * \return
 *  - -1 : Mauvaise longueur de chaine
 *  - -2 : Lorsque indécodables.
 */
int
decode_date (const char *str_ptr, int *JJ, int *MM, int *AAAA)
{
  /* Un pointeur sur un char constant n'est pas un
   * pointeur constant !! */
  const char *c_p;

  if ((strlen (str_ptr) < 8) || (strlen (str_ptr) > 11))
    {
      *JJ = -1;
      *MM = -1;
      *AAAA = -1;
      return -1;
    }
  else
    {
      *JJ = -2;
      *MM = -2;
      *AAAA = -2;
      c_p = str_ptr;
      if (isdigit (*c_p) && isdigit (*(c_p + 1)))
	{
	  *JJ = a_to_int (c_p, 2);
	  c_p += 2;
	  if (is_date_separ (*c_p))
	    c_p++;
	  if (isdigit (*c_p) && isdigit (*(c_p + 1)))
	    {
	      *MM = a_to_int (c_p, 2);
	      c_p += 2;
	      if (is_date_separ (*c_p))
		c_p++;
	      if (isdigit (*c_p) && isdigit (*(c_p + 1)))
		*AAAA = atoi (c_p);
	    }
	}
      else
	{
	  return -2;
	}

      return 0;
    }
}
