/******************************************************************
*
* OPERATOR      Puissance_poly1.c   FUNCTION  ANSI-C
*
* PURPOSE       Puissance_poly1=A.(X/c)^b 
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.0
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_A     Any          Constant coefficient
*             IN   float  Coef_b     Any          Constant coefficient
*             IN   float  Coef_c     Any          Constant coefficient
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
unsigned long
Puissance_poly1 (unsigned long NLoop,
	   const float *Var_in,
           float Coef_A,
           float Coef_b,
           float Coef_c,
           float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
    if ( fabs(Coef_c) > 0)
        {
        Var_out[i] = Coef_A * pow (Var_in[i] / Coef_c, Coef_b);
        }
    else
        Var_out[i] =K_NaN;
    }

  return i;
}


/* la fonction d'enrobage classique */
int
OP_Puissance_poly1 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Puissance_poly1 (%ld ech), calcul de %s par %g*(X/%g)^%g",
		  NbVal, (char *) ArgList[5], *((float *) ArgList[1]), *((float *) ArgList[3]), *((float *) ArgList[2]));

  CodRet = Puissance_poly1 (NbVal, (float *) ArgList[0], *((float *) ArgList[1]), *((float *) ArgList[2]), *((float *) ArgList[3]), (float *) ArgList[7]);

  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Puissance_poly1 (oper * optr)
{
  strcpy (optr->Nom, "Puissance_poly1");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2018-09-05 13:23:40 +0100 (mer. 5 setembre 2018) $";
  optr->fctptr = OP_Puissance_poly1;
  optr->NbArg = 8;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Coef_A */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "any";

  /* Coef_b */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";

  /* Coef_c */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";

  /* Unit_out */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_STRING;
  optr->Arg_Car[4].unite = "any";

  /* Name_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;
  optr->Arg_Car[5].unite = "any";

  /* en_name_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].unite = "any";

  /* Var_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].unite = "$Arg5";
  optr->Arg_Car[7].name = "$Arg6";
  optr->Arg_Car[7].en_name = "$Arg7";

}
