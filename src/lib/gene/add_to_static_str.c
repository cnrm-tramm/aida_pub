/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

/**
 *    Supposons que vous ayez une chaîne dans une zone allouée 
 * de façon statique (s1).
 *    Si vous voulez ajouter une autre chaîne (s2) à la fin, il faut faire:
 *    if (strlen(s2) < (Taille_S1-strlen(s1))
 *      {
 *         strcat (s1, s2);
 *      }
 *      else
 *      {
 *         return, ou break, ou continue, ou exit, ou ....
 *      }
 *
 *   Déjà, c'est du code un peu long, si vous souhaitez ajouter
 * souvent des caractères.
 *   De plus, si s1 est vraiment statique, on ne peut pas l'allonger.
 * Donc le cas du "else" se résume à un traitement d'erreur, et
 * une sortie plus ou moins directe.
 *
 *   La fonction add_to_static_str () est là pour faciliter tout ça.
 * Si il y a assez de place pour faire la concaténation, elle la
 * fait, et renvoie 0.
 * Sinon, elle ne fait rien (pas de copie partielle), et renvoie
 * une valeur non-nulle.
 *
 *   La fonction raconte_GSTR_error () permet d'interpéter le code
 * d'erreur, et d'écrire un message détaillant le problème.
 *
 *   Pour ceux qui ont dimensionné leurs tableaux pour que ça marche
 * toujours, et pour qui le débordement ne devrait être que
 * rarissime (et le symptome d'un problème ailleurs), on fournit
 * aussi la fonction strcat_sur(), qui applique une mesure radicale
 * en cas de débordement : écriture d'un message d'erreur, et exit().
 *
 *
 * NB : il existe des solutions à base de macro, du genre : 
 * #define safe_strcat(x, y) if (strlen(x)+strlen(y)<sizeof(x)) strcat(x, y)
 * mais :
 *  - le traitement de message d'erreur dans le cas "else" alourdi la chose
 *  - sizeof(x) n'est signifiant que dans la fonction où x a été déclaré,
 *  en statique. Ce n'est donc pas vraiment universel.
 *
 * $Log: not supported by cvs2svn $
 * Revision 1.6  2011/01/03 15:58:59  bruno_PIGUET
 * Reformattage commentaires
 *
 * Revision 1.5  2009/04/17 09:11:30  bruno_PIGUET
 * AmÃ©lioration de la doc
 *
 * Revision 1.4  2008/08/29 07:53:31  bruno_PIGUET
 * Le formats des size_t sont %lu au lieu de %d
 *
 * Revision 1.3  2007/11/29 11:50:39  bruno_PIGUET
 * La doc se rapproche d'un format utilisable par doxygen.
 *
 * Revision 1.2  2007/11/29 11:38:39  bruno_PIGUET
 * Corrections de doc.
 *
 * Revision 1.1  2006/11/30 15:07:30  bruno_PIGUET
 * Ajout des ces fonction spour concaténer simplement et proprement des
 * chaînes alloués statiquement (Si c'est trop grand, echec et pas de
 * re-dimensionnement en plus grand).
 *
 *
 */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "add_to_static_str.h"

/**   Concatène 2 chaînes en vérifiant qu'il y a assez de place 
 * disponible.
 *
 * Si il y a assez de place pour faire la concaténation, elle la
 * fait. Sinon, elle ne fait rien (pas de copie partielle).
 *
 * \param s1 : la chaîne qui doit être rallongée.
 * \param  volume_1 : la taille de la mémoire allouée à s1
 * \param s2 : la chaîne qui doit être ajoutée en fin de s1
 *
 * \return 
 *  - 0 en cas de succès
 *  - une valeur non-nulle en cas d'erreur.
 */
int
add_to_static_str (char *s1, size_t volume_1, const char *s2)
{
  size_t len_1;

  if (s1 == NULL)
    return GSTR_INVARG;

  /* les size_t étant souvent unsigned, ce test n'a pas beaucoup d'utilité. 
  if (volume_1 < 0)
    return GSTR_INVARG; */

  /* Par convention, si s2 est NULL, on ne fait rien, 
   * et on dit que ça s'est bien passé.         */
  if (s2 == NULL)
    return 0;

  len_1 = strlen (s1);
  if (len_1 > volume_1 - 1)
    /*s1 est déjà une chaîne qui déborde ! */
    return GSTR_BUGARG;

  if (len_1 + strlen (s2) < volume_1)
    {
      (void) strcat (s1, s2);
      return 0;
    }
  else
    {
      return GSTR_NOSPACE;
    }
}

/** Ecrit sur un fichier un message décrivant un problème
 * survenu à add_to_static_str()
 *
 * @param error : le code de l'erreur survenue
 * @param os : le flux sur lequel le message sera écrit.
 * @param dest : 
 * @param taille : la taille de la mémoire allouée à dest.
 * @param src : pointeur sur la chaine de caracteres qui
 *    devait être copiee à la fin de dest.
 */
void
raconte_GSTR_error (int error, FILE * os, char *dest, size_t taille,
		    const char *src)
{
  size_t i;
  switch (error)
    {
    case 0:
      return;
    case GSTR_INVARG:
      fputs
	("### BUG : La fonction add_to_static_str() a reçu de mauvais arguments \n",
	 os);
      fprintf (os, "          dest = %p", dest);
      if (dest != NULL)
	fprintf (os, " (%s)", dest);
      fputc ('\n', os);
      fprintf (os, "          taille = %lu\n", (unsigned long) taille);
      fprintf (os, "          src = %p", src);
      if (src != NULL)
	fprintf (os, " (%s)", src);
      fputc ('\n', os);
      break;
    case GSTR_BUGARG:
      fputs
	("### BUG : Appel de add_to_static_str() avec une chaîne qui déborde\n",
	 os);
      fprintf (os, "          dest = %p (", dest);
      for (i = 0; i < taille; i++)
	fputc (dest[i], os);
      fputs (")\n", os);
      fprintf (os, "          taille = %lu\n", (unsigned long) taille);
      fprintf (os, "          src = %p (%s)\n", src, (src ? src : ""));
      break;
    case GSTR_NOSPACE:
      fprintf (os,
	       "### PROBLEME : Pas assez de place (%lu) pour concaténer %s et %s\n",
	       (unsigned long) taille, dest, src);
      break;
    default:
      fprintf (os,
	       "### BUG : Erreur inattendue (%d) en retour add_to_static_str()\n",
	       error);
    }
}

/** Ajoute la chaîne src à la fin de la chaîne dest, déjà
 * existante. Si la place allouée à la première chaine
 * n'est pas suffisante, termine le programme.
 *
 * \param dest :  pointeur sur une chaine de caracteres 
 *    qui sera allongee.
 * \param taille : la taille de la mémoire allouée à dest.
 * \param src : pointeur sur la chaine de caracteres qui
 *    doit être copiee à la fin de dest.
 *
 * \return un pointeur sur dest.
 */
char *
strcat_sur (char *dest, size_t taille, const char *src)
{
  int CR;

  CR = add_to_static_str (dest, taille, src);
  if (CR == 0)
    return dest;

  if (stderr != NULL)
    raconte_GSTR_error (CR, stderr, dest, taille, src);

  exit (EXIT_FAILURE);
}
