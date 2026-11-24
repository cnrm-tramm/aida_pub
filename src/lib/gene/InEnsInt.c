/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 *
 * $Log: not supported by cvs2svn $
 * Revision 1.2  1997/02/17 16:05:06  piguet
 * cosmetique
 * */

#include <stdio.h>

/** Cette fonction vérifie qu'un élément entier figure
 * dans un ensemble d'entiers.
 *
 *  @param var : l'élément à tester
 *  @param tab : le tableau contenant tous les entiers de l'ensemble.
 *  @param TailleTab : la taille du tableau. 
 */
int
InEnsInt (int var, int tab[], int TailleTab)
{
  int i;
  for (i = 0; i < TailleTab; i++)
    {
      if (var == tab[i])
	return 1;
    }
/*      (void) fprintf ("%d ne fait pas partie de TAB : {%d, %d,%d}\n",
   VAR, TAB[0], TAB[1], TAB[2]); */
  return 0;
}
