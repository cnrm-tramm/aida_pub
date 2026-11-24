/****************************************************
*
* OPERATOR       Genere_constant.c   FUNCTION  ANSI-C
*
* PURPOSE        Produces a constant serie of type float.

*
* DESCRIPTION    operation arithmetique "+"
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   double time       Any             reference time 
*              IN   float  C          Any             value 
*
*              OUT  float  X                          Result 
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES        
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Genere_constant (unsigned long NLoop,
      const double *time,
      const float C,
      float *X)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *X = C;

      X++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Genere_constant (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec,
		  "Genere_constant, %lu ech, valeur = %g",
		  NbVal, *((float *) ArgList[1]) );

  Genere_constant (NbVal,
	(double *) ArgList[0],
	*((float *)  ArgList[1]),
	(float *) ArgList[2]);
  return OP_OK;
}

void
ID_Genere_constant (oper * optr)
{
  strcpy (optr->Nom, "Genere_constant");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Genere_constant;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */
  optr->repl_oper = "Genere_constant_flt";
  optr->repl_cause = "Ne permet pas de fixer l'unite du parametre calcule";


  /* time */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";
  optr->Arg_Car[0].famille = "any";

  /* C */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = NULL;
  optr->Arg_Car[1].famille = NULL;

  /* X */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.nom";
  optr->Arg_Car[2].unite = "unknown";
  optr->Arg_Car[2].famille = "\"auto\"";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].name = " \"constante\" ";
  optr->Arg_Car[2].en_name = " \"constant\" ";

}
