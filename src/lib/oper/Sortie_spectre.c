/*******************************************************************
* OPERATOR      Sortie_spectre.c FUNCTION ANSI-C
*
* PURPOSE 	Sort un spectre en fichier ascii a partir d'un fichier 2D
*		
* DESCRIPTION	
*		 
* VERSION       1.0
*
* ARGUMENTS     IN   double *  time_rg  second  base de temps
*               IN   float   *  conc2d    any    spectre de concentrations
*               IN   int       nclasses  any    nombre de classes
*               IN   int       taillecl  any    taille des classes en microns
*               IN   long  int tdebut    any    heure du debut d'analyse en secondes depuis minuit
*               IN   long  int tfin      any    heure de fin d'analyse en secondes depuis minuit
*               IN   char   *  nomfich   any    nom du fichier encadre par des guillemets.
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MNP
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include "struct_oper.h"

#include "2D_common.h"

int
Sortie_spectre (const unsigned long int Nloop_rg,
		const double *time_rg,
		const float *conc2d,
		const int nclasses,
		const int taille_classes,
		const long int tdebut,
		const long int tfin,
		const char *nomfich)
{
  FILE *outptr;
  int i, num;
  unsigned long j;
  float *specm2d = NULL;
  long int tdeb, tfi;

  /* Reglage des arguments de temps d'analyse */
  /* Si -1 est specifie, utiliser le debut ou la fin, respectivement */
  /* du set de donnees */
  if (tdebut == -1)
    tdeb = time_rg[0];
  else
    tdeb = tdebut;
  if (tfin == -1)
    tfi = time_rg[Nloop_rg-1];
  else
    tfi = tfin;

  specm2d = malloc(nclasses * sizeof(float));
  if (specm2d == NULL) alloc_error(__FILE__, __LINE__);

  /* Ecriture du spectre moyen sur la periode dans un format ASCII pour xmgrace */
  outptr = fopen(nomfich, "w");
  /* Calcul du spectre moyen */
  for (i=0; i<nclasses; i++) {
    num = 0;
    for (j=0; j<Nloop_rg; j++)
      if (time_rg[j] >= tdeb && time_rg[j] <= tfi) {
	specm2d[i] += conc2d[i+j*nclasses];
	num++;
      }
    specm2d[i] = specm2d[i] / (float) num;
    if (outptr != NULL)
      (void) fprintf(outptr, "%f %e\n", (float) ((i+1)*taille_classes), specm2d[i]/(float)taille_classes);
  }
  if (outptr != NULL)
    (void) fclose(outptr);

  if (specm2d != NULL)
    (void) free(specm2d);
  
  return 0;
}

/* fonction d'enrobage */

int
OP_Sortie_spectre (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Sortie_spectre : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Sortie_spectre (NbVal,
			   (double *) ArgList[0],
			   (float *) ArgList[1],
			   *((int *) ArgList[2]),
			   *((int *) ArgList[3]),
			   *((long int *) ArgList[4]),
			   *((long int *) ArgList[5]),
			   (char *) ArgList[6]);
  
  return OP_OK;
}

void
ID_Sortie_spectre (oper * optr)
{
  int ind;

  strcpy (optr->Nom, "Sortie_spectre");
  optr->Version = "1.0";
  optr->Date = "20/09/01";
  optr->fctptr = OP_Sortie_spectre;
  optr->NbArg = 7;

  ind = 0;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF64;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "second";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "any";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "any";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "any";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_STRING;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";
}
