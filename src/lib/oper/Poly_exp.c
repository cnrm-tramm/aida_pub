/****************************************************
*
* OPERATOR       Poly_exp.c   FUNCTION  ANSI-C
*
* PURPOSE        Fonction exponentielle polynomiale
*
* DESCRIPTION      .....
*                  L'unite du vecteur en sortie fait partie des arguments d'entree
*
* VERSION        1.1
*
* ARGUMENTS    IN    float   Var_In    any     La variable d'entree
*              IN    float   coef_a            coef_a
*              IN    float   coef_b            coef_b
*              IN    float   coef_c            coef_c
*              IN    float   coef_d            coef_d
*              IN    float   coef_e            coef_e
*              IN    char*   unit              unite en sortie 
*              OUT   float   Var_Out           Le resultat
*          
* ENTRY        
*          
* SUBPROGRAMS    
*
* FILES     
*
* REFERENCES 
*
* CHANGES        1.1 Initial release
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

void
Poly_exp (const unsigned long NLoop, const float *Var_In,	/* Variable d'entree */
	  const double coef_a, const double coef_b, const double coef_c,
          const double coef_d, const double coef_e, float *Var_Out)	/* Variable resultat */
{
  unsigned long i;
  double Var_Y;

  for (i = 0; i < NLoop; i++)
    {
      /* Variable Var_Y : variable intermédiaire qui sera ensuite portée puissance e */
      Var_Y = coef_e + *Var_In * (coef_d + *Var_In * coef_c);
      *Var_Out = coef_a + (coef_b * exp (Var_Y));

      Var_In++;
      Var_Out++;
    }
  return;
}

/* la fonction d'enrobage classique */

int
OP_Poly_exp (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec,
           "Poly_exp, NbVal=%lu, calcul de y(%s) = %g + %g*e^(%g*x^2+%g*x+%g)",
	   NbVal, (char *) ArgList[6], *((double *) ArgList[1]),
	   *((double *) ArgList[2]), *((double *) ArgList[3]),
           *((double *) ArgList[4]), *((double *) ArgList[5]));

  Poly_exp (NbVal,
	    (float *) ArgList[0],
	    *((double *) ArgList[1]),
	    *((double *) ArgList[2]),
	    *((double *) ArgList[3]),
	    *((double *) ArgList[4]),
	    *((double *) ArgList[5]),
            (float *) ArgList[7]);
  return OP_OK;
}

void
ID_Poly_exp (oper * optr)
{
  strcpy (optr->Nom, "Poly_exp");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_exp;
  optr->NbArg = 8;

  /* Var_In */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* coef_a */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* coef_b */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";

  /* unit_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].unite = "";

  /* Var_Out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  /* l'unite est obligatoirement l'unite donne en 7ime argument  */
  optr->Arg_Car[7].unite = "$Arg7";
  optr->Arg_Car[7].famille = "$Arg1.famille";

}
