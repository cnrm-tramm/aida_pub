/****************************************************
*
* OPERATOR      PolyCal2.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute second order polynomial function of "float" variables
*
* DESCRIPTION   Standard calculation...
*
* VERSION       1.5
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X^2
*             OUT  float  Var_out  same as 2      Result
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       1.4   Adapted to new def. of categorie in Arg_profil
*               1.3   gave standard name to ID_PolyCal2 function
*               1.2   switched args order/added comments
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "Poly_2_flt.h"


/* la fonction d'enrobage classique */
int
OP_PolyCal2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;

  NCar = sprintf (DiagExec, "PolyCal2 : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  /* La vraie fonction de calcul est la même que celle de Poly_2_flt() */
  Poly_2_flt (NbVal,
	      (float *) ArgList[0],
	      *((float *) ArgList[1]),
	      *((float *) ArgList[2]),
	      *((float *) ArgList[3]),
	      (float *) ArgList[4]);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_PolyCal2 (oper * optr)
{
  strcpy (optr->Nom, "PolyCal2");
  optr->Version = "1.5";
  optr->Date = "08/26/96";
  optr->fctptr = OP_PolyCal2;
  optr->repl_oper = "Poly_2_flt";
  optr->repl_cause = "ne permet pas de fixer l’unite du parametre calcule";
  optr->NbArg = 5;

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
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "unknown";
  optr->Arg_Car[4].famille = "\"auto\"";

}
