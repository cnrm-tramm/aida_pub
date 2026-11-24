/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/** Concatène dynamiquement 3 chaînes de caractères.
 *
 * Cette fonction renvoie un pointeur vers une nouvelle
 * chaîne de caractère contenant la concaténation des
 * trois chaînes s1, s2 et s3. La nouvelle chaîne est allouée
 * par malloc(), et doit donc être libérée ultérieurement
 * par free().
 * 
 * \param s1 : la première chaîne.
 * \param s2 : la seconde chaîne.
 * \param s3 : la troisieme chaîne.
 *
 * \return Cette fonction renvoie un pointeur sur la nouvelle
 *   chaîne, ou NULL s'il n'y avait pas assez de mémoire.
 * 
 * TODO : fonction variadique complète : char *strconcat(const char *first, ...)
 * en utilisant va_arg() et compagnie (<stdarg.h>).
 */
char *
strconcat3 (const char *const s1, const char *const s2, const char *const s3)
{
  char *retval;

  /* Pas de test : if (s[123] != NULL) 
   * Ne soyons pas plus royaliste que le roi.
   * Si le système est tolérant, la suite se passera bien.
   * Si le système n'est pas tolérant, l'erreur qu'on
   * aurait évitée ici se produira plus tard...
   */
  retval = malloc (strlen (s1) + strlen (s2) + strlen (s3) + 1);
  if (retval == NULL)
    return NULL;

  strcpy (retval, s1);
  strcat (retval, s2);
  strcat (retval, s3);
  return retval;
}
