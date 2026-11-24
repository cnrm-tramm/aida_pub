#include <sys/stat.h>

/** Essaie d'ajouter les droits "mode" à l'élément désigné par 
 * "path" (fichier ou répertoire).
 *
 * \param path : chemin d'un fichier ou d'un répertoire.
 * \param mode : Les droits à ajouter, sous la forme d'un entier 
 * au format demandé par chmod(2) ou du champ st_mode de la structure
 *   remplie par stat(2).
 *
 * \return : 0 si OK,  -1 en cas d'echec (code d'erreur dans errno).
 */
int
try_add_rights (const char *path, int mode)
{
  struct stat sb;

  if (stat (path, &sb) == -1)
    {
      return -1;
    }

  return chmod (path, sb.st_mode | mode);
}
