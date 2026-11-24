/****************************************************
*
* OPERATOR      Poly_2_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute 2nd order polynomial function of "float" variables
* OBJECTIF      Application d'un polynome de 2nd degré à un parametre "float"
*
* DESCRIPTION   Standard calculation...
*
* VERSION       1.0
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X^2
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
* CHANGES      creation 09/05/2001 
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */
void
Poly_2_flt (unsigned long NLoop,
	    const float *Var_in,
	    float Coef_0,
            float Coef_1,
            float Coef_2,
            float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *Var_out = Coef_0 + *Var_in * (Coef_1 + *Var_in * Coef_2);

      Var_in++;
      Var_out++;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_Poly_2_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec,
		  "Poly_2_flt, %lu echant., calcul de y = %g + %g x + %g x^2, resultat en %s",
		  NbVal, *((float *) ArgList[1]), *((float *) ArgList[2]),
		  *((float *) ArgList[3]), (char *) ArgList[4]);

  Poly_2_flt (NbVal,
	      (float *) ArgList[0],
	      *((float *) ArgList[1]),
	      *((float *) ArgList[2]),
	      *((float *) ArgList[3]), (float *) ArgList[5]);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly_2_flt (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Poly_2_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_2_flt;
  optr->NbArg = 6;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Coef_0 to Coef_2 */
  for (i = 1; i < 4; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
    }

  /* unit_out */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_STRING;

  /* Var_out */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg5";
  optr->Arg_Car[5].famille = "\"auto\"";
}
