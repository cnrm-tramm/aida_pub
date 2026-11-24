#define _POSIX_SOURCE 1

#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

#define DIR_FORCE 1


/** Vérifie que l'argument "DirPath" correspond bien à un répertoire.
 * Si il n'existe pas et si mode == DIR_FORCE, il essaie de le créer
 *
 * @param DirPath : Le chemin à tester
 * @param mode : indicateur de mode de fonctionnement (force la création ou non)
 * 
 * \return
 *   -  1 si le rep. existe
 *   -  0 si il n'existe pas
 */
int
CheckDirExist (const char *DirPath, int mode)
{
  struct stat buf;
  int CodRet;

  CodRet = stat (DirPath, &buf);
  if (CodRet == 0)
    {				/* Il existe, mais est-ce un répertoire ?? */
      if (S_ISDIR (buf.st_mode))
	return 1;
      else
	return 0;
    }
  else
    {				/* Existe pas, alors essayons de le créer    */
      if (errno == ENOENT)
	{
	  if (mode == DIR_FORCE)
	    {
	      /* Les droits demandés dans l'appel ci-dessous sont illusoires
	       *  car :
	       *  «Sous Linux, à part les bits de permission, seul le bit 
	       *  de mode S_ISVTX est honoré. C'est-à-dire que sous Linux,
	       *  le répertoire réellement créé prend le mode 
	       *  (mode & ~umask & 01777) »    */
	      CodRet = mkdir (DirPath,
			      S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IWGRP
			      | S_IXGRP);
	      if (CodRet == 0)
		return 1;
	      else
		return 0;
	    }
	}
      else
	return 0;
    }
  /* Si on arrive ici, Y'a du souci à se faire ... */
  return 0;
}
