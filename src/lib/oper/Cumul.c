/****************************************************
*
* OPERATOR      Cumul.c   FUNCTION  ANSI-C
*
* PURPOSE       Calcul de la série temporelle de X cumulé,
*               en considérant les valuers manquante comme 0
*
* DESCRIPTION   Calcul de la serie de cumul du paramètre X 
*		 X_cumul[i] = X[i] + X_cumul[i-1]
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  X        any        Original data
*             OUT  float  X_cumul  same as 1  Cumulated data
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

unsigned long
Cumul (unsigned long Nbval, const float *X, float *X_cumul)
{
  unsigned long i;
  unsigned long nb_NaN;

  if (Nbval == 0)
    return 0;			/* Pas touche à X_cumul, lui aussi de taille nulle ! */

  if (isfinite (X[0]))
    {
      X_cumul[0] = X[0];
      nb_NaN = 0;
    }
  else
    {
      X_cumul[0] = 0.;
      nb_NaN = 1;
    }

  for (i = 1; i < Nbval; i++)
    {
      if (isfinite (X[i]))
	{
	  X_cumul[i] = X[i] + X_cumul[i - 1];
	}
      else
	{
	  X_cumul[i] = X_cumul[i - 1];
	  nb_NaN += 1;
	}
    }

  return nb_NaN;
}

/* la fonction d'enrobage classique */

int
OP_Cumul (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  CodRet = Cumul (NbVal, (float *) ArgList[0], (float *) ArgList[1]);

  if (CodRet == 0)
    sprintf (DiagExec, "0 valeurs manquantes dans la série");
  else
    sprintf (DiagExec, "%lu valeurs manquante (consideree == 0)", CodRet);

  return OP_OK;
}

void
ID_Cumul (oper * optr)
{
  strcpy (optr->Nom, "Cumul");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cumul;
  optr->NbArg = 2;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* X_cumul */
  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "$Arg1.famille";

}
