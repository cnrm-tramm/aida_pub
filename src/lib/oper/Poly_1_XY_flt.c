/******************************************************************
*
* OPERATOR      Poly_1_XY_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute 1srt order polynomial function of two "float" variables
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  X          Any          "X" value
*             IN   float  Y          Any          "Y" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_X     Any          coefficient of X
*             IN   float  Coef_Y     Any          coefficient of Y
*             IN   string unit_out                Unit of the result
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
* CHANGES       1
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

/* La vraie fonction... */
unsigned long
Poly_1_XY_flt (unsigned long NLoop,
	    const float *X,
	    const float *Y,
	    const float Coef_0,
	    const float Coef_X,
	    const float Coef_Y,
	    float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      Var_out[i] = Coef_0 + X[i] * Coef_X + Y[i] * Coef_Y;
    }
  return i;
}

/* la fonction d'enrobage classique */

int
OP_Poly_1_XY_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, 
                  "Poly_1_XY_flt, %lu echant., calcul de  z = %g + %g x + %g y",
                  NbVal, 
                  *((float *) ArgList[2]), *((float *) ArgList[3]), 
                  *((float *) ArgList[4]));

  /** Le lecteur attentif aura remarqué que l'argument Nr 5
   * n'est pas passé à la routine de calcul. En fait, il ne sert
   * qu'à remplir le champ "unit" du vecteur de sortie.
   */
  CodRet = Poly_1_XY_flt (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       *((float *) ArgList[2]),
		       *((float *) ArgList[3]),
		       *((float *) ArgList[4]),
		       (float *) ArgList[6]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly_1_XY_flt (oper * optr)
{
  int idx=0;
  strcpy (optr->Nom, "Poly_1_XY_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_1_XY_flt;
  optr->NbArg = 7;

  /* X */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Y */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Coef_0 */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Coef_X */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Coef_Y */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* unit_out */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_STRING;
  optr->Arg_Car[idx].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Var_out */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].unite = "$Arg6";
  optr->Arg_Car[idx].famille = " \"auto\" ";

}
