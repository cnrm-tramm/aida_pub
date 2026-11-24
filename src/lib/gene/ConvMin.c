/* 
 * $Log: not supported by cvs2svn $
 * Revision 1.3  2007/11/23 12:59:50  bruno_PIGUET
 * Documentation au format "proche javadoc" pour Doxygen
 *
 * Revision 1.2  1997/02/17 16:04:59  piguet
 * cosmetique
 */

#include <ctype.h>

/** Convertit en minuscule tous les caractères de la chaîne
 * passée en argument.  
 *
 * C'est une conversion sur place : Il n'y a pas d'allocation de
 * nouvelle chaîne, la chaîne passée en argument est modifiée.
 * Il n'y a pas de protection contre le cas où la chaîne
 * à convertir est NULL.
 *
 * @param string : Chaîne de caractère à convertir.
 * */

void
ConvMin (char *string)
{
  while (*string)
    {
      *string = tolower (*string);
      string++;
    }
}
