/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/** Concatène dynamiquement 2 chaînes de caractères.
 *
 * Cette fonction renvoie un pointeur vers une nouvelle
 * chaîne de caractère contenant la concaténation des
 * deux chaînes s1 et s2. La nouvelle chaîne est allouée
 * par malloc(), et doit donc être libérée ultérieurement
 * par free().
 * 
 * \param s1 : la première chaîne.
 * \param s2 : la seconde chaîne.
 *
 * \return Cette fonction renvoie un pointeur sur la nouvelle
 *   chaîne, ou NULL s'il n'y avait pas assez de mémoire.
 * 
 * TODO : fonction variadique complète : char *strconcat(const char *first, ...)
 * en utilisant va_arg() et compagnie (<stdarg.h>).
 */
char *
strconcat2 (const char *s1, const char *s2)
{
  char *retval;

  /* Pas de test : if (s[12] != NULL) 
   * Ne soyons pas plus royaliste que le roi.
   * Si le système est tolérant, la suite se passera bien.
   * Si le système n'est pas tolérant, l'erreur qu'on
   * aurait évitée ici se produira plus tard...
   */
  retval = malloc (strlen (s1) + strlen (s2) + 1);
  if (retval == NULL)
    return NULL;

  strcpy (retval, s1);
  strcat (retval, s2);
  return retval;
}
