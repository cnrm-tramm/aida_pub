/*
 *  Écriture d'un fichier de description de
 * l'interface d'appel (API) des opérateurs, à partir des
 * fonctions d'auto-description (les ID_xxx).
 */

#define _POSIX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#ifndef PATH_MAX
#define PATH_MAX 1023
#endif

#include <gene.h>
#include <rapt.h>
#include <oper.h>

#include "load_oper.h"

char
CatCode (const CATEGORIE categorie)
{
  switch (categorie)
    {
    case CAT_UNKNOWN:
      return 'U';
    case VECTOR:
      return 'V';
    case COEFFICIENT:
      return 'C';
    default:
      return 'B';
    }
}

char
DirCode (const sens direction)
{
  switch (direction)
    {
    case DIR_NONE:
      return 'U';
    case DIR_IN:
      return 'I';
    case DIR_OUT:
      return 'O';
    default:
      return 'B';
    }
}

int
EcritDescOperAPI (FILE * DescFile, const oper * Oper)
{
  int j;
  const Arg_profil *Arg_Car;

  if (DescFile == NULL)
    return 0;

  if (Oper == NULL)
    {
      (void) fprintf (DescFile, "# %s\n",
		      "AUTOMATICALLY GENERATED : do not edit");
      (void) fprintf (DescFile, "# %s\n",
		      "re-generate with : oper_API_write");
      (void) fprintf (DescFile, "# %s;%s;[%s%s%s\"[\"%s\"]\";]\n", "<Name>",
		      "<NbArg>", "<arg_way>", "<arg_category>", "<arg_type>",
		      "<arg_dim>");
      return 0;
    }

  (void) fprintf (DescFile, "%s;%d;", Oper->Nom, Oper->NbArg);
  for (j = 0; j < Oper->NbArg; j++)
    {
      Arg_Car = &(Oper->Arg_Car[j]);
      /* Le sens */
      (void) fputc (DirCode (Arg_Car->direction), DescFile);
      /* La categorie */
      (void) fputc (CatCode (Arg_Car->categorie), DescFile);
      /* Le type */
      (void) fputs (AidaTypNom (Arg_Car->typ), DescFile);
      (void) fprintf (DescFile, "[%s]", Arg_Car->array_dim);
      (void) fputc (';', DescFile);
    }
  (void) fprintf (DescFile, "\n");

  return 1;
}

int
main (int argc, char *argv[])
{
  oper *Liste_oper;
  int i, NbOper, NbEcrit;
  const char *OperLibPath = "./liboper.sl";	/* Travail dans le rep. courant */
  const char *DescFileName = "oper_API_desc.txt";
  FILE *DescFile;

  NbOper = Init_Liste_Oper_dyn (OperLibPath, &Liste_oper);
  if (NbOper < 0)
    {
      (void) fprintf (stderr,
		      "%s: Impossible de charger la bibliotheque d'operateurs %s \n",
		      argv[0], OperLibPath);
      (void) fprintf (stderr, "---%s---\n", OPLD_erreur (NbOper));
      /* CloseLog (); */
      exit (4);
    }
  else
    {
      (void) fprintf (stdout,
		      "--- %s : %d opérateurs chargés depuis %s\n",
		      argv[0], NbOper, OperLibPath);
    }

  /* Le fichier de description */
  DescFile = fopen (DescFileName, "w");
  if (DescFile == NULL)
    {
      perror (DescFileName);
      return EXIT_FAILURE;
    }

  EcritDescOperAPI (DescFile, NULL);
  NbEcrit = 0;
  for (i = 0; i < NbOper; i++)
    {
      NbEcrit += EcritDescOperAPI (DescFile, &(Liste_oper[i]));
    }
  (void) fclose (DescFile);

  (void) fprintf (stdout, "--- %s : %d opérateurs décrits dans %s\n",
		  argv[0], NbEcrit, DescFileName);
  Free_Liste_Oper (&Liste_oper);

  return EXIT_SUCCESS;
}
