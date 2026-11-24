/****************************************************
*
* OPERATOR      Som_1D20.c   FUNCTION  ANSI-C
*
* PURPOSE       Sum consecutives values of a time serie
*
* DESCRIPTION   Routine de sommation, pour variables 1D (Int16)
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   float  NbSum    without      frequency ratio
*             OUT  float  Var_out    same as 1  Summed data
*
* REFERENCES
*
* CHANGES     
*              
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include "struct_oper.h"

#include "Som_1D.h"


/* la fonction d'enrobage classique */

int
OP_Som_1D20 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Som_1D20 : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Som_1D (NbVal,
		     (short *) ArgList[0],
		     20,
		     *((float *) ArgList[1]),
		     *((int *) ArgList[2]),
		     (short *) ArgList[3]);

  if (DiagExec != NULL)
    switch (CodRet)
      {
      case 0:
	return OP_OK;
      case -1:
	sprintf (DiagExec, "NbSum < 1 !!!");
	return OP_FAIL;
      case -2:
	sprintf (DiagExec, "malloc Error !");
	return OP_FAIL;
      default:
	sprintf (DiagExec, "Erreur %d", CodRet);
	return OP_FAIL;
      }
  return OP_OK;

}

void
ID_Som_1D20 (oper * optr)
{
  strcpy (optr->Nom, "Som_1D20");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Som_1D20;
  optr->NbArg = 4;

  /*  Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "20";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /*  NbSum */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /*  Decal */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_I16;
  optr->Arg_Car[3].array_dim = "20";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal / $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample / $Arg2";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";

}
