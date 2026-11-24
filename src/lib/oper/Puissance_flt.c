/******************************************************************
*
* OPERATOR      Puissance_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute puissance of "float" variables
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.5
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   string unit_out                Unit of the result
*             IN   string name_out                Name of the result
*             IN   string en_name_out             English name of the result
*
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

/* La vraie fonction de calcul */
#include "Puissance.h"

/* la fonction d'enrobage classique */
int
OP_Puissance_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Puissance_flt (%ld ech), calcul de %s par X^%g",
		  NbVal, (char *) ArgList[3], *((float *) ArgList[1]));

  CodRet = Puissance (NbVal,
		      (float *) ArgList[0],
		      *((float *) ArgList[1]), (float *) ArgList[5]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Puissance_flt (oper * optr)
{
  strcpy (optr->Nom, "Puissance_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Puissance_flt;
  optr->NbArg = 6;

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
  optr->Arg_Car[1].unite = "any";

  /* Unit_out */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].unite = "any";

  /* Name_out */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].unite = "any";

  /* en_name_out */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_STRING;
  optr->Arg_Car[4].unite = "any";

  /* Var_out */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].unite = "$Arg3";
  optr->Arg_Car[5].name = "$Arg4";
  optr->Arg_Car[5].en_name = "$Arg5";

}
