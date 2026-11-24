/****************************************************
*
* OPERATOR      Poly_5_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute 5th order polynomial function of "float" variables
* OBJECTIF      Application d'un polynome de 5ieme degré à un parametre "float"
*
* DESCRIPTION   Standard calculation...
*
* VERSION       1.0
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X^2
*             IN   float  Coef_3     Any          coefficient of X^3
*             IN   float  Coef_4     Any          coefficient of X^4
*             IN   float  Coef_5     Any          coefficient of X^5
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

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */
void
Poly_5_flt (unsigned long NLoop,
	    const float *Var_in,
	    float Coef_0,
	    float Coef_1,
	    float Coef_2,
	    float Coef_3, float Coef_4, float Coef_5, float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *Var_out =
	Coef_0 + *Var_in * (Coef_1 +
			    *Var_in * (Coef_2 +
				       *Var_in * (Coef_3 +
						  *Var_in * (Coef_4 +
							     *Var_in *
							     Coef_5))));

      Var_in++;
      Var_out++;
    }
  return;
}


/* la fonction d'enrobage classique */
int
OP_Poly_5_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec,
		  "Poly_5_flt, %lu echant., calcul de y = %g + %g x + %g x^2 + %g x^3 + %g x^4 +%g x^5, %s",
		  NbVal, *((float *) ArgList[1]),
		  *((float *) ArgList[2]),
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]),
		  *((float *) ArgList[5]),
		  *((float *) ArgList[6]), (char *) ArgList[7]);

  Poly_5_flt (NbVal,
	      (float *) ArgList[0],
	      *((float *) ArgList[1]),
	      *((float *) ArgList[2]),
	      *((float *) ArgList[3]),
	      *((float *) ArgList[4]),
	      *((float *) ArgList[5]),
	      *((float *) ArgList[6]), (float *) ArgList[8]);

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly_5_flt (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Poly_5_flt");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 aoÃ»t 2012) $";
  optr->fctptr = OP_Poly_5_flt;
  optr->NbArg = 9;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* C_0 à C_5 */
  for (i = 1; i < 7; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
    }

  /* unit_out */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_STRING;

  /* Var_out */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg7";
  optr->Arg_Car[8].famille = "\"auto\"";

}
