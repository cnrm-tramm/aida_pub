/******************************************************************
*
* OPERATOR      Log_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       The Log_flt operator returns log(a*Var_In + b)+c
* 		 when Var_In is a "float" variable
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          coefficient of Log
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          Constant coefficient (bias)
*             IN   float  Coef_3     Any          Constant coefficient (lag)
*             IN   string unit_out                Unit of the result
*             IN   string name_out                Name of the result
*             IN   string en_name_out             English name of the result
*             OUT  float  Var_out  		  Result
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

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */
unsigned long
Log_flt (unsigned long NLoop,
	 const float *Var_in,
	 const double Coef_0,
	 const double Coef_1,
	 const double Coef_2, const double Coef_3, float *Var_out)
{
  unsigned long i, nb_neg = 0;
  double tmp;

  for (i = 0; i < NLoop; i++)
    {
      tmp = Var_in[i] * Coef_1 + Coef_2;
      if (tmp <= 0.0)
	{
	  nb_neg++;
	}
      Var_out[i] = Coef_0 * log (tmp) + Coef_3;
    }
  return nb_neg;
}


/* la fonction d'enrobage classique */

int
OP_Log_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec,
		  "Log_flt, %lu echant., calcul de %s (\"%s\") par y = %g * log(%g * x + %g) + %g",
		  NbVal, (char *) ArgList[6], (char *) ArgList[5],
		  *((double *) ArgList[1]), *((double *) ArgList[2]),
		  *((double *) ArgList[3]), *((double *) ArgList[4]));

  /** Le lecteur attentif aura remarqué que les arguments Nr 6, 7, 8 (ArgList[5], ArgList[6], ArgList[7])
   * ne sont pas passés à la routine de calcul. En fait, il ne servent
   * qu'à remplir les champs "unit", "name", "english_name" du vecteur de sortie.
   */
  CodRet = Log_flt (NbVal,
		    (float *) ArgList[0],
		    *((double *) ArgList[1]),
		    *((double *) ArgList[2]),
		    *((double *) ArgList[3]),
		    *((double *) ArgList[4]), (float *) ArgList[8]);

  (void) sprintf (DiagExec + strlen (DiagExec),
		  ", %lu calculs impossibles (log(neg))", CodRet);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Log_flt (oper * optr)
{
  strcpy (optr->Nom, "Log_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Log_flt;
  optr->NbArg = 9;

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
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "any";

  /* Coef_1 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "any";

  /* Coef_2 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "any";

  /* Coef_3 */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;
  optr->Arg_Car[5].unite = "any";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_STRING;
  optr->Arg_Car[7].unite = "any";

  /* Var_out */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  optr->Arg_Car[8].unite = "$Arg6";
  optr->Arg_Car[8].name = "$Arg7";
  optr->Arg_Car[8].en_name = "$Arg8";
  optr->Arg_Car[8].famille = "$Arg1.famille";
}
