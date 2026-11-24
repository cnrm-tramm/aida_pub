
/*
 * $Log: not supported by cvs2svn $
 * Revision 1.5  2007/11/23 12:59:50  bruno_PIGUET
 * Documentation au format "proche javadoc" pour Doxygen
 *
 * Revision 1.4  2002/04/05 17:46:35  tramm
 * Ajout protection contres arguments NULL
 *
 * Revision 1.3  2000/08/04  14:54:36  14:54:36  piguet (Bruno PIGUET)
 * Passage de nonsig en const
 * 
 * Revision 1.2  97/02/17  16:05:08  16:05:08  piguet (Bruno PIGUET)
 * cosmetique
 */

#include <string.h>

/** Enlève, dans "string", tous les caractères de
 * "nonsig" consécutifs situés à la FIN.
 *
 *    La chaine "string" est donc MODIFIÉE.
 * Par exemple,
 *   str = "bla-bla  ";
 *   OteFin    (str, " ");
 *   printf ("%s\n", str), donne "bla-bla"
 *
 *   \param string : la chaîne à nettoyer.
 *   \param nonsig : une chaîne contenant tous les caractères
 * considérés non-significatifs.
 */
void
OteFin (char *string,
	const char *nonsig)
{
  char *p2;

  /* Recherche du dernier char "not in" nonsig
   * Pour le premier, on utilisait strspn.
   * comme strrspn n'a pas l'air d'exister, on le fait "a la main" */

  if (string == NULL)
    return;

  if (nonsig == NULL)
    return;

  p2 = &string[strlen (string) - 1];
  while ((p2 >= string) && (strchr (nonsig, (int) *p2) != NULL))
    p2--;
  /* Ici, on a :
   *       soit p2 < string (et p2 pointe a string-1)
   *       soit *p2 not in nonsig
   *   Donc, dans TOUS LES CAS, on peut dire que la fin
   * de la chaine "significative" est a (p2+1)
   */
  *(p2 + 1) = 0;
}
