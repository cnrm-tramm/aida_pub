/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>

/** Teste l'existence d'un fichier
 * 
 * \param path: le chemin à tester
 *
 * \return 1 si le path correspond à un fichier (ou un lien)
 *    0 dans le cas d'un fichier inexistant.
 *  -1 dans les autres cas (autre chose  qu'un fichier, pas d'accès au path)
 * 
 */
int
file_exists (const char *const path)
{
  struct stat sb;

  /* Pas de test : if (path != NULL) 
   * Ne soyons pas plus royaliste que le roi.
   * Si le système est tolérant, la suite se passera bien.
   * Si le système n'est pas tolérant, l'erreur qu'on
   * aurait évitée ici se produira plus tard...
   */
  if (stat (path, &sb) == 0)
    {
      /* Quelque chose existe à cet endroit */
      if (S_ISREG (sb.st_mode) || S_ISLNK (sb.st_mode))
	return 1;
      else      /* Ça existe et ce n'est pas un fichier */
	return -1;
    }
  /* On est en erreur (Ces  appels système retournent zéro s'ils réussissent)
   *  En cas d'échec, et errno contient le code de l'erreur.
   */
  if (errno == ENOENT)
    return 0;

  return -1;
}
