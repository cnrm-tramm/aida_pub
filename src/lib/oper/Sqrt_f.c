/****************************************************
*
* OPERATOR       Sqrt_f.c   FUNCTION  ANSI-C
*
* PURPOSE        Computation of square root of float values
*
* DESCRIPTION      .....
*                  .....
*
* VERSION        1.4
*
* ARGUMENTS    IN    float   Var_In    any     La variable d'entree
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
* CHANGES        1.3 adapted to "categorie"'s definition change.
*                1.2 added args' sampling description.
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

long
Sqrt_f (unsigned long NLoop,
	const float *Var_In,	/* Variable d'entree */
	float *Var_Out)		/* Variable resultat */
{
  unsigned long i, Nb_neg;

  Nb_neg = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (*Var_In < 0.0)
	Nb_neg++;

      /* Si *Var_In est négative, on laisse la librairie math. mettre un NaN. */
      *Var_Out = sqrt (*Var_In);

      Var_In++;
      Var_Out++;
    }
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Sqrt_f (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;

  sprintf (DiagExec, "OP_Sqrt_f, NbVal=%lu;", NbVal);

  CodRet = Sqrt_f (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1]);

  sprintf (DiagExec + strlen (DiagExec), " %ld X<0", CodRet);
  return OP_OK;
}

void
ID_Sqrt_f (oper * optr)
{
  strcpy (optr->Nom, "Sqrt_f");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Sqrt_f;
  optr->NbArg = 2;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].famille = "any";

  /* Var_out */
  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  /* l'unite se deduit de l'entree  */
  optr->Arg_Car[1].unite = "$Arg1.unit";
  /* WARN : above formula should be "sqrt($Arg1.unit)". It will be so    */
  /* when the interpreter will handle the sqrt function applied to units */
  optr->Arg_Car[1].famille = "\"auto\"";

}
