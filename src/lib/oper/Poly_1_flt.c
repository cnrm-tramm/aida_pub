/******************************************************************
*
* OPERATOR      Poly_1_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute 1srt order polynomial function of "float" variables
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   string unit_out                Unit of the result
*             IN   string name_out                Name of the result
*             IN   string en_name_out             English name of the result
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
Poly_1_flt (unsigned long NLoop,
	    const float *Var_in,
	    const float Coef_0,
	    const float Coef_1,
	    float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      Var_out[i] = Coef_0 + Var_in[i] * Coef_1;
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Poly_1_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Poly_1_flt, %lu echant., calcul de %s (\"%s\") par y = %g + %g x",
		  NbVal, (char *) ArgList[4], (char *) ArgList[5],
                  *((float *) ArgList[1]), *((float *) ArgList[2]));

  /** Le lecteur attentif aura remarqué que les arguments Nr 3, 4, 5
   * ne sont pas passé à la routine de calcul. En fait, il ne servent
   * qu'à remplir les champs "unit", "name", "english_name" du vecteur de sortie.
   */
  CodRet = Poly_1_flt (NbVal,
		       (float *) ArgList[0],
		       *((float *) ArgList[1]),
		       *((float *) ArgList[2]),
		       (float *) ArgList[6]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly_1_flt (oper * optr)
{
  strcpy (optr->Nom, "Poly_1_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_1_flt;
  optr->NbArg = 7;

  /* Var_in */
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
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_STRING;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].unite = "$Arg4";
  optr->Arg_Car[6].name = "$Arg5";
  optr->Arg_Car[6].en_name = "$Arg6";
  optr->Arg_Car[6].famille = "\"auto\"";

}
