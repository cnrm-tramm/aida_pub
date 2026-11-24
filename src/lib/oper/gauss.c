/******************************************************************
*
* OPERATOR      gauss.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute gaussian function of "float" variables
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value (centree)
*             IN   float  coeff_0     Any          Constant coefficient
*             IN   float  coeff_1     Any          coefficient of X
*             IN   float  coeff_2     Any          coefficient of X*X
*             IN   float  coeff_3     Any          coefficient of exp(Y)
*             IN   float  coeff_4     Any          coeff_add of X for Y
*             IN   float  coeff_5     Any          coeff_divi of X for Y
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
gauss (unsigned long NLoop,
       const float *Var_in,
       const float coeff_0,
       const float coeff_1,
       const float coeff_2,
       const float coeff_3,
       const float coeff_4, 
       const float coeff_5, 
       float *Var_out)
{
  unsigned long i;
  float y;

  for (i = 0; i < NLoop; i++)
    {
      y = (Var_in[i] + coeff_4) / coeff_5;
      Var_out[i] = coeff_3 * exp (y * y / -2) + coeff_0 + 
	           Var_in[i] * (coeff_1 + coeff_2 * Var_in[i]);
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_gauss (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec,
		  "gauss(%lu ech) coefs = %g, %g, %g, %g, %g, %g, %s",
		  NbVal, 
		  *((float *) ArgList[1]), *((float *) ArgList[2]),
		  *((float *) ArgList[3]), *((float *) ArgList[4]),
		  *((float *) ArgList[5]), *((float *) ArgList[6]),
		  (char *)ArgList[7]);

/*
 * Le lecteur attentif aura remarqué que l'argument Nr 7
 * n'est pas passé à la routine de calcul. En fait, il ne sert
 * qu'à remplir le champ "unit" du vecteur de sortie.
 */
  CodRet = gauss (NbVal,
		  (float *) ArgList[0],
		  *((float *) ArgList[1]),
		  *((float *) ArgList[2]),
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]),
		  *((float *) ArgList[5]),
		  *((float *) ArgList[6]), (float *) ArgList[8]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_gauss (oper * optr)
{
  strcpy (optr->Nom, "gauss");
  optr->Version = "1.5";
  optr->Date = "01/22/08";
  optr->fctptr = OP_gauss;
  optr->NbArg = 9;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_STRING;
  optr->Arg_Car[7].type_sample = NULL;	/* sans signification pour STRING */
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "any";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  optr->Arg_Car[8].unite = "$Arg4";
  optr->Arg_Car[8].famille = " \"auto\" ";

}
