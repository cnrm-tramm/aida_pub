/****************************************************
*
* OPERATOR       Ech.c   FUNCTION  ANSI-C
*
* PURPOSE        Sampling of a time serie
*
* DESCRIPTION    Routine d'echantillonnage, pour variables "float". 
*                ressort 1 valeur toutes les (1/RapFreq), en commencant 
*                par la "decal"ieme. 
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   float  Var_in     any        Original data
*            IN   double RapFreq    whithout   frequency ratio
*            IN   int    Decal      sec/freq   delay between first values
*            OUT  float  Var_out    same as 1  Sampled data
*
* REFERENCES
*
* CHANGES        1.3 adapted to CATEGORIE's definition change
*                1.2 added comments/switched arg. orders
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
long
Ech (unsigned long Nloop,
     const float *Var_in,
     const double RapFreq,
     const int Decal,
     float *Var_out,
     long Tab_CR[3])

/*     Routine d'echantillonnage, pour variables "float".
 *  Ressort 1 valeur toutes les (1/RapFreq), en commencant
 *  par la "decal"ieme.
 */

{
  unsigned long i;
  int NSom;
  long Ntour, Reste;

  if ((RapFreq > 1.0) || (RapFreq < 0.0))
    {
      return -1;
    }

  NSom = floor ((1.0 / RapFreq) + 0.5);
  Ntour = Nloop / NSom;		/* division entière car opérandes entiers */
  Reste = Nloop % NSom;

  if ((Decal < 0) || (Decal > NSom))
    return -2;

  Var_in += Decal;

  for (i = 0; i < Ntour; i++)
    {
      *Var_out = *Var_in;
      Var_in += NSom;
      Var_out++;
    }

  if (Reste > 0)
    {
      if (Decal < Reste)
	{
	  *Var_out = *Var_in;
	}
      else
	{
	  /* Pour être cohérent avec le cas Decal<0,
	   * on pourraît, peut-être, recopier la dernière valeur. */
	  *Var_out = K_NaN;
	}
    }

  Tab_CR[0] = NSom;
  Tab_CR[1] = Ntour;
  Tab_CR[2] = Reste;

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Ech (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int N_char;
  long Tab_CR[3];

  N_char = sprintf (DiagExec, "OP_Ech, NbVal=%ld, ", NbVal);
  DiagExec += N_char;

  CodRet = Ech (NbVal,
		(float *) ArgList[0],
		*((double *) ArgList[1]),
		*((int *) ArgList[2]),
		(float *) ArgList[3],
		Tab_CR);

  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK : %ld val. calculées, (%lu = %ld*%ld+%ld).",
		      Tab_CR[1], NbVal, Tab_CR[1], Tab_CR[0], Tab_CR[2]);
      return OP_OK;
    }

  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "Error : RapFreq >1 ou <0");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "Error : Decal hors [0, 1/RapFreq] : %d",
		    *((int *) ArgList[2]) );
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Error : code %ld", CodRet);
      return OP_FAIL;
    }
}

void
ID_Ech (oper * optr)
{
  strcpy (optr->Nom, "Ech");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ech;
  optr->NbArg = 4;
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
  optr->Arg_Car[1].typ = ATYC_IF64;
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

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].name = "$Arg1.name";
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[3].sample = "$Arg1.sample * $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
