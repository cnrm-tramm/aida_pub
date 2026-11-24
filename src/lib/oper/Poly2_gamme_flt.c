/******************************************************************
*
* OPERATOR      Poly2_gamme_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Calcul d'un polynome du second degre dans une certaine
*               gamme. En dehors, interpolation lineaire.
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
              IN   float  borne_min  Any          Seuil inférieur de la gamme
              IN   float  borne_max  Any          Seuil supérieur de la gamme
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X²
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
Poly2_gamme_flt (unsigned long NLoop,
		 const float *Var_in,
		 const float b_min,
		 const float b_max,
		 const float Coef_0,
		 const float Coef_1,
		 const float Coef_2,
		 float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if (Var_in[i] < b_min)
	{
	  Var_out[i] = (Coef_0 + b_min * (Coef_1 + b_min * Coef_2)) * Var_in[i] / b_min;
	}
      else if (Var_in[i] > b_max)
	{
	  Var_out[i] = (Coef_0 + b_max * (Coef_1 + b_max * Coef_2)) * Var_in[i] / b_max;
	}
      else
	{
	  Var_out[i] = Coef_0 + Var_in[i] * (Coef_1 + Var_in[i] * Coef_2);
	}
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Poly2_gamme_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Poly2_gamme_flt : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

/*
 * Le lecteur attentif aura remarqué que l'argument Nr 6
 * n'est pas passé à la routine de calcul. En fait, il ne sert
 * qu'à remplir le champ "unit" du vecteur de sortie.
 */
  CodRet = Poly2_gamme_flt (NbVal,
			    (float *) ArgList[0],
			    *((float *) ArgList[1]),
			    *((float *) ArgList[2]),
			    *((float *) ArgList[3]),
			    *((float *) ArgList[4]),
			    *((float *) ArgList[5]),
			    (float *) ArgList[7]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly2_gamme_flt (oper * optr)
{
  strcpy (optr->Nom, "Poly2_gamme_flt");
  optr->Version = "1.5";
  optr->Date = "08/26/96";
  optr->fctptr = OP_Poly2_gamme_flt;
  optr->NbArg = 8;
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
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].unite = "$Arg7";

}
