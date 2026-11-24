/****************************************************
*
* OPERATOR      Set_freqech_reftime.c   FUNCTION  ANSI-C
*
* PURPOSE       Change freq_ech and ref_time fields of the header
*
* DESCRIPTION   
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  X    	      any        Original data
*             IN   double freq_ech    Hz   	Value of freq_ech to set
*             OUT  float  Y    	      same as X 
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

long
Set_freqech_reftime (unsigned long NbVal,
     float *X,
     float freq_ech ,
     float *Y)
{
  long i;

 
  for (i =0 ; i < NbVal; i++)
    {
     Y[i] = X[i];
    }
  return(0);
}

/* la fonction d'enrobage classique */

int
OP_Set_freqech_reftime (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  CodRet = Set_freqech_reftime (NbVal,
		(float *) ArgList[0],
		*((float *) ArgList[1]),
		(float *) ArgList[2]);

  return (OP_OK);
}

void
ID_Set_freqech_reftime (oper * optr)
{
  strcpy (optr->Nom, "Set_freqech_reftime");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Set_freqech_reftime;
  optr->NbArg = 3;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg2";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = " \"reftime_TIME_\" + $Arg2";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";
}
