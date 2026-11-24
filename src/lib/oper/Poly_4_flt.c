/****************************************************
*
* OPERATOR      Poly_4_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute 4ieme! order polynomial function of "float" variables
* OBJECTIF      Application d'un polynome de 4ieme degré à un parametre "float"
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
unsigned long
Poly_4_flt (unsigned long NLoop,
	    const float *Var_in,
	    float Coef_0,
	    float Coef_1,
	    float Coef_2, 
	    float Coef_3, 
	    float Coef_4, 
	    float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *Var_out =
	Coef_0 + *Var_in * (Coef_1 +
			    *Var_in * (Coef_2 +
				       *Var_in * (Coef_3 +
						  *Var_in * Coef_4)));

      Var_in++;
      Var_out++;
    }
  return i;
}


/* la fonction d'enrobage classique */
int
OP_Poly_4_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec,
		  "Poly_4_flt, %lu echant., calcul de y = %g + %g x + %g x^2 + %g x^3 + %g x^4, %s",
		  NbVal, *((float *) ArgList[1]),
          *((float *) ArgList[2]),
		  *((float *) ArgList[3]),
          *((float *) ArgList[4]),
		  *((float *) ArgList[5]),
          (char *) ArgList[6]);

  CodRet = Poly_4_flt (NbVal,
		       (float *) ArgList[0],
		       *((float *) ArgList[1]),
		       *((float *) ArgList[2]),
		       *((float *) ArgList[3]),
		       *((float *) ArgList[4]),
		       *((float *) ArgList[5]),
		       (float *) ArgList[7]);
  if (CodRet == NbVal)
    {
      return OP_OK;
    }
  else
    {
      strcat (DiagExec, "On a vu un passage de neutrino supraluminique !");
      return OP_FAIL;
    }
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly_4_flt (oper * optr)
{
  strcpy (optr->Nom, "Poly_4_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_4_flt;
  optr->NbArg = 8;

  /* Var_in */
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

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;

  /* unit_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;

  /* Var_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg7";
  optr->Arg_Car[7].famille = "\"auto\"";

}
