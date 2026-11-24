/******************************************************************
*
* OPERATOR      PolyCal1_dbl.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute 1srt order polynomial function of "double" variables
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.5
*
* ARGUMENTS   IN   double  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             OUT  double  Var_out  same as 2      Result
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
*               1.3   gave standard name to ID_PolyCal1_dbl function
*               1.2   switched args order/added comments
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "Poly_1_dbl.h"

/* la fonction d'enrobage classique */

int
OP_PolyCal1_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "PolyCal1_dbl : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  /* Le calcul est le même que celui de Poly_1_dbl() */
  CodRet = Poly_1_dbl (NbVal,
			 (double *) ArgList[0],
			 *((double *) ArgList[1]),
			 *((double *) ArgList[2]),
			 (double *) ArgList[3]);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_PolyCal1_dbl (oper * optr)
{
  strcpy (optr->Nom, "PolyCal1_dbl");
  optr->Version = "1.5";
  optr->Date = "08/26/96";
  optr->fctptr = OP_PolyCal1_dbl;
  optr->repl_oper = "Poly_1_dbl";
  optr->repl_cause = "ne permet pas de fixer l’unite du parametre calcule";
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "unknown";

}
