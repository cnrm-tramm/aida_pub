/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8 
 *
 * $Log: not supported by cvs2svn $
 * Revision 1.1  2011/03/29 08:48:53  bruno_PIGUET
 * Ajout de ConvMajPrem() et des test associés.
 *                                                          
 */

#include <ctype.h>
#define NULL (void *)0

/** Convertit en majuscule le premier caractere non-espace de la chaîne
 * passée en argument.
 *
 * C'est une conversion sur place : Il n'y a pas d'allocation de
 * nouvelle chaîne, la chaîne passée en argument est modifiée.
 *
 * @param string : Chaîne de caractère à convertir.
 */

void
ConvMajPrem (char *string)
{
  if (string == NULL)
    return;

  while (isspace (*string))
    {
      string++;
    }
  *string = toupper (*string);
}
