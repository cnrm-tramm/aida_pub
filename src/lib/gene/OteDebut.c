/*
 * $Log: not supported by cvs2svn $
 * Revision 1.4  2002/04/05 17:46:05  tramm
 * Ajout protection contres arguments NULL
 *
 * Revision 1.3  2000/08/04  14:22:57  14:22:57  piguet (Bruno PIGUET)
 * Passage de "nonsig" en const char *
 * 
 * Revision 1.2  97/02/17  16:05:07  16:05:07  piguet (Bruno PIGUET)
 * cosmetique
 */

#include <string.h>

/** Enlève, dans "string", tous les caractères de
 * "nonsig" consécutifs situés au DÉBUT.
 *
 *    La chaîne "string" est donc MODIFIÉE.
 * Par exemple, le bout de code suivant :
 *    str = "  bla-bla";
 *    OteDebut  (str, " ");
 *    printf ("%s\n", str);
 * produit le résultat "bla-bla"
 *
 * \param string : la chaîne à nettoyer.
 * \param nonsig : une chaîne contenant tous les caractères
 * considérés non-significatifs.
 */
void
OteDebut (char *string,
	  const char *nonsig)
{
  size_t ind_deb;
  char *p1, *p2;

  /* On recherche le premier char "not in" nonsig */

  if (string == ((void *) 0))
    return;

  if (nonsig == NULL)
    return;

  ind_deb = strspn (string, nonsig);

  /* et on deplace les characteres */
  p2 = &string[ind_deb];
  p1 = string;

  /* On ne fait le deplacement que si il y a qqchose a faire    */
  /* Il faut s'arreter APRES que l'on ait copie le char "0" dans *p1 */

  if (p2 != p1)
    do
      {
	*p1++ = *p2;
      }
    while (*p2++ != 0);
}
