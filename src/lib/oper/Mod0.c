/****************************************************
*
* OPERATOR       Mod0.c   FUNCTION  ANSI-C
*
* PURPOSE        Calcul de X - (X[0](modulo M))
*
* DESCRIPTION    Attention : pour convertir un temps GPS en UTC, utiliser GPS_to_UTC
*
* VERSION        1.0
*
* ARGUMENTS    IN   float  X    Any             first value
*              IN   float  M    Any             modulo value
*              OUT  float  Z    Any		Result
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES              
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


void
Mod0 (unsigned long NLoop, float *X,	/* en ... any */
      float M,			/* en ... any  */
      float *Z)
{
  unsigned long i;

  float offset;

  /* Calcul d'un offset sur le premier non-nul */
  i = 0;
  while ((X[i] == 0) && (i < NLoop))
    i++;
  offset = (float) (M * (floor (X[i] / M)));

  for (i = 0; i < NLoop; i++)
    {
      *Z = (*X) - offset;
      Z++;
      X++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Mod0 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  sprintf (DiagExec, "Mod0, modulo %f, NbVal=%lu\n", *((float *) ArgList[1]),
	   NbVal);

  Mod0 (NbVal,
	(float *) ArgList[0], *((float *) ArgList[1]), (float *) ArgList[2]);
  return OP_OK;
}

void
ID_Mod0 (oper * optr)
{
  strcpy (optr->Nom, "Mod0");
  optr->Version = "1.0";
  optr->Date = "03/18/98";
  optr->fctptr = OP_Mod0;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";

}
