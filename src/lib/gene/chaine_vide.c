
/*
 * $Log: not supported by cvs2svn $
 * Revision 1.1  2004/03/05 11:21:50  piguet
 * Initial revision
 *
 */

#include <string.h>

/** Teste si une chaîne est un pointeur vide ou constituée que d'espace ou de TAB
 *
 * @param string : la chaîne à tester.
 *
 * \return 
 *   - 1 si la chaine n'est constituée que d'espace ou de TAB
 *   - 0 sinon.
 */
int
chaine_vide (const char *string)
{
  /* On recherche le premier char "not in" nonsig */

  if (string == ((void *) 0))
    return 1;

  while (*string != 0)
    {
      if ((*string != ' ') && (*string != '\t'))
	return 0;
      string++;
    }
  return 1;
}
