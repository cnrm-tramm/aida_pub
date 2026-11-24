#include <string.h>
#include <stdio.h>

/**   Cette fonction découpe (éclate) un "Path" complet 
 *  en 3 parties (éventuellement vides) :
 *  - le répertoire
 *  - le nom de fichier sans extension
 *  - l'extension (la partie du nom située apres le dernier point)
 *
 *  Chacun des trois pointeurs vers tableau de car. destiné à 
 *  contenir un résultat (dir, base, et ext) peut être NULL : 
 *   il ne sera alors pas rempli.
 *
 * @param path : chaine de caractère contenant le chemin complet (ne sera pas modifiée)
 * @param dir : pointeur sur une chaîne de caractères qui sera remplie
 *       avec la valeur du répertoire.
 * @param base :  pointeur sur une chaîne de caractères qui sera remplie
 *       avec la base du nom de fichier 
 * @param ext :  pointeur sur une chaîne de caractères qui sera remplie
 *       avec l'extension.
 *
 *  ATTENTION : Cette fonction remplit les trois zones mémoires
 *   pointées par "dir", "base" et "ext" sans pouvoir vérifier qu'elles
 *   sont suffisament grandes. C'est à l'appelant de s'en assurer.
 *
 *   $Log: not supported by cvs2svn $
 *   Revision 1.4  2007/08/01 11:33:56  bruno_PIGUET
 *   Ajout, pour des trois pointeurs vers tableau de car.  destinés à
 *   contenir un résultat de "eclat()", de la possibilité d'être NULL :
 *   il ne sera alors simplement pas rempli.
 *
 *   Revision 1.3  2007/08/01 11:00:32  bruno_PIGUET
 *   Mise en forme : accents Iso8859-1 (au lieu de HP-roman-8), commentaires
 *   se rapprochant du style JavaDoc/Doxygen.
 *
 *   Revision 1.2  1997/02/17 16:05:08  piguet
 *   cosmetique
 */
void
eclat (const char *path, char *dir, char *base, char *ext)
{
  char *DerPoint;
  const char *DebBase;

  /* DebBase = 1er car après dernier Slash, ou alors début chaine */
  DebBase = strrchr (path, '/');
  if (DebBase == NULL)
    {
      DebBase = path;
    }
  else
    {
      DebBase++;
    }

  /* Faut-il fournir "dir" ? */
  if (dir != NULL)
    {
      if (DebBase == path)
	{
	  /* dir est vide */
	  strcpy (dir, "");
	}
      else
	{
	  /* recopiage dir */
	  strncpy (dir, path, (size_t) (DebBase - path));
	  dir[DebBase - path] = 0;	/* strncpy() ne le met pas toujours */
	}
    }

  /* recherche dernier point */
  DerPoint = strrchr (DebBase, '.');

  if (DerPoint == NULL)
    {
      /* recopiage basename */
      if (base != NULL)
	{
	  strcpy (base, DebBase);
	}
      /* ext se réduit à rien */
      if (ext != NULL)
	{
	  strcpy (ext, "");
	}
    }
  else
    {
      /* recopiage basename, et le cas basename="" est bien traité */
      if (base != NULL)
	{
	  strncpy (base, DebBase, (size_t) (DerPoint - DebBase));
	  base[DerPoint - DebBase] = 0;	/*idem sur strncpy */
	}
      /* recopiage ext */
      if (ext != NULL)
	{
	  strcpy (ext, DerPoint + 1);
	}
    }
}
