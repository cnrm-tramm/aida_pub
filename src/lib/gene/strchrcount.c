/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <stddef.h>

/** Compte le nombre d'occurence du caractère c dans la chaine s.
 *
 * \param s : la chaîne à analyser.
 * \param c : le caractère à compter.
 *
 * \return le nombre d'occurence de c dans s.
 * 
 */
size_t
strchrcount (const char *s, char c)
{
  size_t n = 0;

  /* Pas de test : if (s != NULL) 
   * Ne soyons pas plus royaliste que le roi.
   * Si le système est tolérant, la suite se passera bien.
   * Si le système n'est pas tolérant, l'erreur qu'on
   * aurait évitée ici se produira plus tard...
   */
  while (*s != 0)
    {
      if (*s == c)
	n++;
      s++;
    }
  return n;
}
