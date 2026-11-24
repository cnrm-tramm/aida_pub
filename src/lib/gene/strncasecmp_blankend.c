/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <string.h>
#include <strings.h>

/**  Compare les deux chaînes s1 et s2, en ignorant
 * les différences entre majuscules et minuscules, en se
 * limitant aux n premiers caractères de s1, mais en 
 * ne déclarant les chaînes égales que si les éventuels
 * caractères de s1 après le n-ième sont des espaces
 * ou des tabulations.
 *
 * \param s1 : la première chaîne à comparer
 * \param s2 : la seconde chaîne à comparer
 * \param n : le nombre de caractères à prendre en compte.
 *
 * \return  un entier négatif,  nul,  ou  positif,  si  la  chaîne  s1
 *             est respectivement inférieure, égale ou supérieure à s2.
 * 
 */
int
strncasecmp_blankend (const char *s1, const char *s2, size_t n)
{
  int CR;
  /* Pas de test : if (s1 != NULL) 
   * Ne soyons pas plus royaliste que le roi :
   * Si le système est tolérant, la suite se passera bien.
   * Si le système n'est pas tolérant, l'erreur qu'on
   * aurait évitée ici se produira plus tard...
   */

  CR = strncasecmp (s1, s2, n);
  if ((CR == 0) && (strlen (s1) > n))
    {
      while (s1[n] != 0)
	{
	  if ((s1[n] != ' ') && (s1[n] != '\t'))
	    {
	      CR = n;
	      break;
	    }
	  n++;
	}
    }
  return CR;
}
