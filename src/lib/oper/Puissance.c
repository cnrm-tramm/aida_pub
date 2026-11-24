/******************************************************************
*
* OPERATOR      Puissance.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute puissance of "float" variables
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.5
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             OUT  float  Var_out    none         Result
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

/* La vraie fonction... */
unsigned long
Puissance (unsigned long NLoop,
	   const float *Var_in,
           float Coef_0,
           float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      Var_out[i] = pow (Var_in[i], Coef_0);
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Puissance (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Puissance (%ld ech), calcul de X^%g", NbVal,
		  *((float *) ArgList[1]));

  CodRet = Puissance (NbVal,
		      (float *) ArgList[0],
		      *((float *) ArgList[1]),
                      (float *) ArgList[2]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Puissance (oper * optr)
{
  strcpy (optr->Nom, "Puissance");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Puissance;
  optr->NbArg = 3;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Coef_0 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "any";

  /* Var_out */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].name = "$Arg1.name a la puisssance $Arg2";
  optr->Arg_Car[2].en_name = "";

}
