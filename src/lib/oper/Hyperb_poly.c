/****************************************************
*
* OPERATOR      Hyperb_poly.c   FUNCTION  ANSI-C
*
* PURPOSE       Computes a composition of hyperbolic and polynomial functions
*
* OBJECTIF      Calcul d'une loi hyperbolique (en 1/x) après application de polynomes
*
* DESCRIPTION   Y = (a + b x) / (c + d x)
*
* VERSION       1.0
*
* ARGUMENTS   IN   float  X_in      Any       X value
*             IN   float  Coef_a    Any       Constant coefficient in numerator
*             IN   float  Coef_b    Any       coefficient of X in numerator
*             IN   float  Coef_c    Any       Constant coefficient in denominator
*             IN   float  Coef_d    Any       coefficient of X  in denominator
*             IN   string unit_out            Unit of the result
*             OUT  float  X_out    unit_out   Result
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES      $Log: not supported by cvs2svn $
* CHANGES      Revision 1.1  2011/04/28 15:25:26  bruno_PIGUET
* CHANGES      Ajout de l'opÃ©rateur Hyperb_poly.
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
#include "struct_oper.h"

/* La vraie fonction... */
int
Hyperb_poly (unsigned long NLoop,
		 const float *X_in,
		 float Coef_a,
		 float Coef_b, float Coef_c, float Coef_d, float *X_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *X_out = (Coef_a + Coef_b * *X_in) / (Coef_c + Coef_d * *X_in);

      X_in++;
      X_out++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Hyperb_poly (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec,
		  "Hyperb_poly, %lu echant., calcul de y = (%g + %g x) / (%g + %g x) unit=%s",
		  NbVal, *((float *) ArgList[1]), *((float *) ArgList[2]),
		  *((float *) ArgList[3]), *((float *) ArgList[4]), (char*) ArgList[5]);


  CodRet = Hyperb_poly (NbVal,
			    (float *) ArgList[0],
			    *((float *) ArgList[1]),
			    *((float *) ArgList[2]),
			    *((float *) ArgList[3]),
			    *((float *) ArgList[4]), 
                (float *) ArgList[8]);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Hyperb_poly (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Hyperb_poly");
  optr->Version = "$Revision: 6777 $";
  optr->Date = "$Date: 2017-04-26 16:52:35 +0200 (mer. 26 avril 2017) $";
  optr->fctptr = OP_Hyperb_poly;
  optr->NbArg = 9;

  /* X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Coef_a to Coef_d */
  for (i = 1; i < 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
    }

  /* unit_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;

  /* name_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;

  /* en_name_out */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_STRING;

  /* X_out */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg6";
  optr->Arg_Car[8].name = "$Arg7";
  optr->Arg_Car[8].en_name = "$Arg8";
  optr->Arg_Car[8].famille = "$Arg1.famille";
}
