/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/** Enrobe ("wrap") une chaîne de caractère dynamique par un début et une fin.
 *
 * Cette fonction renvoie un pointeur vers une nouvelle chaîne de
 * caractère contenant la concaténation des trois chaînes
 * before, s et after. 
 * L'ancienne chaîne est libérée par free(), elle doit donc avoir été 
 * allouée par malloc(), et ne plus servir après.
 * La nouvelle chaîne est allouée * par malloc(), et doit donc être 
 * libérée ultérieurement par free().
 * Utilisation : si s a été allouée dynamiquement, et ne doit plus
 * resservir, la syntaxe la plus simple et la plus naturelle est :
 *   s = strwrap("deb", s, "fin"); 
 * 
 * \param before: la partie initiale de l'enrobage.
 * \param s : la chaîne à enrober.
 * \param after : la partie finale de l'enrobage.
 *
 * \return Cette fonction renvoie un pointeur sur la nouvelle
 *   chaîne, ou NULL s'il n'y avait pas assez de mémoire.
 * 
 */
char *
strwrap (const char *const before, char ** s, const char *const after)
{
  char *retval;

  /* Pas de test : if (s != NULL) 
   * Ne soyons pas plus royaliste que le roi.
   * Si le système est tolérant, la suite se passera bien.
   * Si le système n'est pas tolérant, l'erreur qu'on
   * aurait évitée ici se produira plus tard...
   */
  retval = malloc (strlen (before) + strlen (*s) + strlen (after) + 1);
  if (retval == NULL)
    return NULL;

  strcpy (retval, before);
  strcat (retval, *s);
  strcat (retval, after);
  free (*s);
  *s = NULL;
  return retval;
}
