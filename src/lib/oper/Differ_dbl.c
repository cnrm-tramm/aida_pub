/****************************************************
*
* OPERATOR      Differ_dbl.c   FUNCTION  ANSI-C
*
* PURPOSE       Derivate a time serie  
*
* DESCRIPTION   Calcule la série des différences consécutives d'une 
*            variable "double".
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   double  X	       unite     	Original data
*             OUT  float  diffX 	unite/s  	differentiated data
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */

long
Differ_dbl (unsigned long NbVal, double *X, float *diff_X)
{
  unsigned long i;

  if (NbVal == 0)
    return 1;
    
  /* La première valeur est forcément manquante */
  diff_X[0] = K_NaN;

  /* boucle */
  for (i = 1; i < NbVal; i++)
    {
      diff_X[i] = X[i] - X[i-1];
    }

  return 1;
}

/* la fonction d'enrobage classique */

int
OP_Differ_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Differ_dbl (%lu ech)", NbVal);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Differ_dbl (NbVal,
			(double *) ArgList[0],
		       	(float *) ArgList[1]);

  if (CodRet > 0)
    return OP_OK;
  else
    return OP_FAIL;
}

void
ID_Differ_dbl (oper * optr)
{
  strcpy (optr->Nom, "Differ_dbl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Differ_dbl;
  optr->NbArg = 2;

  /*  X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* diff_X */
  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].unite = "$Arg1.unit ";
  optr->Arg_Car[1].famille = "auto";
  optr->Arg_Car[1].name = "\"Difference consecutive de \" + $Arg1.name";
  optr->Arg_Car[1].en_name = " \"Running difference of \" + $Arg1.english_name";
}
