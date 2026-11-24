/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8 
 */

#define _POSIX_SOURCE

#include <ctype.h>
#include <string.h>
#include <stdlib.h>

/** Retourne "vrai" si le caractère passé
 * en argument est un délimiteur d'heure valide.
 */
static int
is_heure_separ (int c)
{
  return (c == ':');
}

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

/**  Interprète une chaîne de type :
 * digit/digit[/separ]/digit/digit[/separ/]digit/digit[/radix/digit/digit/digit]
 * sous la forme de deux entiers positifs et d'un
 * nombre real : HH MM et secondes.
 *  Les séparateurs peuvent être ":" ou "h" puis "m" puis "s"
 *
 * Pour l'instant, pas de controles des bornes (du genre MM<=60)
 *
 * Codes retours :
 *    -1 : Mauvaise longueur de chaine
 *    -2 : Lorsque indécodables.
 */
int
decode_heure (const char *str_ptr,
	      int *HH,
	      int *MM,
	      double *sec)
{
  /* Un pointeur sur un char constant n'est pas un
   * pointeur constant !! */
  const char *c_p;

  if ((strlen (str_ptr) < 6)
      || (strlen (str_ptr) > 12))
    {
      *HH = -1;
      *MM = -1;
      *sec = -1;
      return -1;
    }
  else
    {
      *HH = -2;
      *MM = -2;
      *sec = -2;
      c_p = str_ptr;
      if (isdigit (*c_p) && isdigit (*(c_p + 1)))
	{
	  *HH = a_to_int (c_p, 2);
	  c_p += 2;
	  if (is_heure_separ (*c_p) || (*c_p == 'h'))
	    c_p++;
	  if (isdigit (*c_p) && isdigit (*(c_p + 1)))
	    {
	      *MM = a_to_int (c_p, 2);
	      c_p += 2;
	      if (is_heure_separ (*c_p) || (*c_p == 'm'))
		c_p++;
	      if (isdigit (*c_p) && isdigit (*(c_p + 1)))
		*sec = atof (c_p);
	    }
	}
      else
	{
	  return -2;
	}

      return 0;
    }
}
