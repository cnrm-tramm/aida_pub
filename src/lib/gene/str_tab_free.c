
#include <stdlib.h>

/** Libération mémoire d'un tableau de chaînes allouées dynamiquement.
 *
 * \param str_tab :
 * \param n :
 */
void
str_tab_free (char **str_tab, size_t n)
{
  size_t i;
  for (i = 0; i < n; i++)
    {
      /* Petit service rendu à l'appelant : si certains
       * éléments du tableau sont déjà libérés, on les 
       * ignore silencieusement. */
      if (str_tab[i] != NULL)
	{
	  free (str_tab[i]);
	  str_tab[i] = NULL;
	}
    }
}
