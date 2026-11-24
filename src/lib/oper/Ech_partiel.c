/****************************************************
*
* OPERATOR       Ech_partiel.c   FUNCTION  ANSI-C
*
* PURPOSE        Sampling of a time serie
*
* DESCRIPTION    Routine d'echantillonnage, pour variables "float". 
*                ressort N valeurs toutes les M, en commencant 
*                par la "decal"ieme. 
*                Typiquement M=Freq_ech (ou sample), et 0<N<M
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   float  Var_in     any        Original data
*            IN   int    N          count      
*            IN   int    M          count      
*            IN   int    Decal      count      delay between first values
*            OUT  float  Var_out    same as 1  Sampled data
*
* REFERENCES
*
* CHANGES        1.1 
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */

int
Ech_partiel (unsigned long Nloop,
	     const float *Var_in,
	     const int N,
	     const int M,
	     const int Decal,
	     float *Var_out)

/*     Routine d'echantillonnage, pour variables "float".
 *  Ressort N valeur toutes les M, en commencant
 *  par la "decal"ieme.
 */

{
  unsigned long i;
  int j;

  if (M < 0)
    {
      return -1;
    }
  if ((N > M) || (N < 0))
    {
      return -2;
    }
  if ((Decal < 0) || (Decal > M))
    {
      return -3;
    }

  Var_in += Decal;

  for (i = 0; i < ((Nloop - Decal) / M); i++)
    {
      for (j = 0; j < N; j++)
	{
	  *Var_out = *Var_in;
	  Var_in++;
	  Var_out++;
	}
      Var_in += (M - N);
    }

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Ech_partiel (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Ech_partiel, NbVal=%lu, selectionne %d/%d valeurs, à partir de la %d",
                      NbVal,
                      *((int *) ArgList[1]),
                      *((int *) ArgList[2]),
                      *((int *) ArgList[3]));

  CodRet = Ech_partiel (NbVal,
			(float *) ArgList[0],
			*((int *) ArgList[1]),
			*((int *) ArgList[2]),
			*((int *) ArgList[3]),
			(float *) ArgList[4]);
  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec + strlen (DiagExec), "OK");
      return OP_OK;
    case -1:
      sprintf (DiagExec + strlen (DiagExec), "Error : M <0");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec + strlen (DiagExec), "Error : N >M ou <0");
      return OP_FAIL;
    case -3:
      sprintf (DiagExec + strlen (DiagExec), "Error : Decal hors [0, M]");
      return OP_FAIL;
    default:
      return OP_FAIL;
    }
}

void
ID_Ech_partiel (oper * optr)
{
  strcpy (optr->Nom, "Ech_partiel");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ech_partiel;
  optr->NbArg = 5;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].famille = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[1].unite = "without";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].name = "$Arg1.name";
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal * $Arg2 / $Arg3";
  optr->Arg_Car[4].sample = "$Arg1.sample * $Arg2 / $Arg3";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = " \"time_\" + $Arg5.sample";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";

}
