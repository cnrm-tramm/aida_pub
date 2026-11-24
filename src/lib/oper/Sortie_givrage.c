/*******************************************************************
* OPERATOR      Sortie_givrage.c FUNCTION ANSI-C
*
* PURPOSE 	Sort un indice de givrage base sur les donnees du 2D-C et de temperature
*               en format ascii
*		
* DESCRIPTION	
*		 
* VERSION       1.0
*
* ARGUMENTS     IN   double *  time_rg  second  base de temps
*               IN   float  *  fractc    any    fraction de particules spheriques
*               IN   float  *  temperature any  temperature en Celcius
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

int
Sortie_givrage (const unsigned long int Nloop_rg,
		const double *time_rg,
		const float *fractc,
		const float *tempe,
		const long int tdebut,
		const long int tfin,
		const char *nomfich)
{
  FILE *outptr;
  unsigned long j;
  long int tdeb, tfi;
  float sec;
  int hour, min;

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

  /* Ecriture du temps u la presomption de givrage selon le 2D-C est importante */
  outptr = fopen(nomfich, "w");
  (void) fprintf(outptr, "TEMPS FRACT TEMPE HEURE MIN SEC\n\n");
  for (j=0; j<Nloop_rg; j++)
    if (time_rg[j] >= tdeb && time_rg[j] <= tfi)
      if (tempe[j] <= 0.0 && fractc[j] >= 0.15) {
	hour = (int) (time_rg[j] / 3600.0);
	min = (int) ( ( time_rg[j] - ((float)hour*3600.0) ) / 60.0);
	sec = time_rg[j] - ((float)hour*3600.0) - ((float)min*60.0);
	(void) fprintf(outptr, "%f %f %f %d %d %f\n", time_rg[j], fractc[j], tempe[j], hour, min, sec);
      }
  if (outptr != NULL)
    (void) fclose(outptr);
  
  return 0;
}

/* fonction d'enrobage */

int
OP_Sortie_givrage (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Sortie_givrage : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Sortie_givrage (NbVal,
			   (double *) ArgList[0],
			   (float *) ArgList[1],
			   (float *) ArgList[2],
			   *((long int *) ArgList[3]),
			   *((long int *) ArgList[4]),
			   (char *) ArgList[5]);
  
  return OP_OK;
}

void
ID_Sortie_givrage (oper * optr)
{
  int ind;

  strcpy (optr->Nom, "Sortie_givrage");
  optr->Version = "1.0";
  optr->Date = "20/10/01";
  optr->fctptr = OP_Sortie_givrage;
  optr->NbArg = 6;

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
