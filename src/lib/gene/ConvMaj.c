/* 
 * $Log: not supported by cvs2svn $
 * Revision 1.5  2011/08/31 10:21:34  bruno_PIGUET
 * Modif formelle pour eviter que CVS cree des ligne de log commencant
 * toutes comme un commenatire, par '/' suivi de '*'.
 *
 * Revision 1.4  2007/11/23 12:32:49  bruno_PIGUET
 * Documentation au format quasi-javadoc pour Doxygen.
 *
 * Revision 1.3  1997/02/17 16:12:22  piguet
 * pour voir...
 *
 * Revision 1.2  97/02/17  16:04:50  16:04:50  piguet (Bruno PIGUET)
 * cosmetique
 *                                                          
 */

#include <ctype.h>

/** Convertit en majuscule tous les caractères de la chaîne
 * passée en argument.
 *
 * C'est une conversion sur place : Il n'y a pas d'allocation de
 * nouvelle chaîne, la chaîne passée en argument est modifiée.
 * Il n'y a pas de protection contre le cas où la chaîne
 * à convertir est NULL.
 *
 * @param stringmin : Chaîne de caractère à convertir.
 */

void
ConvMaj (char *stringmin)
{
  while (*stringmin)
    {
      *stringmin = toupper (*stringmin);
      stringmin++;
    }
}
