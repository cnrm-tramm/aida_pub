/****************************************************
*
* OPERATOR       Pow_f.c   FUNCTION  ANSI-C
*
* PURPOSE        The Pow_f operator returns a vector containing the
*                values of : base**(Var_In + scale)
*
* DESCRIPTION      .....
*                  .....
*
* VERSION        1.1
*
* ARGUMENTS    IN    float   Var_In    any     La variable d'entree
*              IN    float   Base              X
*              IN    float   Scale             D
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
Pow_f (const unsigned long NLoop,
       const float *Var_In,	/* Variable d'entree */
       const double base,
       const double scale,
       float *Var_Out)		/* Variable resultat */
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *Var_Out = pow (base, *Var_In + scale);

      Var_In++;
      Var_Out++;
    }
  return;
}

/* la fonction d'enrobage classique */

int
OP_Pow_f (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec,
           "Pow_f, NbVal=%lu, calcul de %g^(x+%g)",
           NbVal,
	   *((double *) ArgList[1]), *((double *) ArgList[2]));

  Pow_f (NbVal,
	 (float *) ArgList[0],
	 *((double *) ArgList[1]),
	 *((double *) ArgList[2]),
	 (float *) ArgList[3]);
  return OP_OK;
}

void
ID_Pow_f (oper * optr)
{
  strcpy (optr->Nom, "Pow_f");
  optr->Version = "1.1";
  optr->Date = "08/26/96";
  optr->fctptr = OP_Pow_f;
  optr->NbArg = 4;

  /* Var_In */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].famille = "any";

  /* base */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* scale */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* Var_Out */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  /* l'unite se deduit de l'entree  */
  /* TODO : A Corriger   */
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
