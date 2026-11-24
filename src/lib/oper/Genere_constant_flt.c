/****************************************************
*
* OPERATOR       Genere_constant_flt.c   FUNCTION  ANSI-C
*
* PURPOSE        Produces a constant serie of type float.

*
* DESCRIPTION    operation arithmetique "+"
*
* VERSION       $Revision: 5243 $
*
* ARGUMENTS    IN   double time       Any             reference time 
*              IN   float  C          Any             value 
*              IN   string unit                       Unit of the constant
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

#include "Genere_constant.h"

/* la fonction d'enrobage classique */

int
OP_Genere_constant_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec,
		  "Genere_constant_flt, %lu ech, valeur = %g, unite=%s",
		  NbVal, *((float *) ArgList[1]), (char *) ArgList[2]);

  /* La fonction qui travaille, c'est la même que celle de l'operateur Genere_constant () */
  Genere_constant (NbVal,
		   (double *) ArgList[0],
		   *((float *) ArgList[1]), (float *) ArgList[3]);
  return OP_OK;
}

void
ID_Genere_constant_flt (oper * optr)
{
  strcpy (optr->Nom, "Genere_constant_flt");
  optr->Version = "$Revision: 5243 $";
  optr->Date = "$Date: 2013-07-12 10:37:36 +0200 (ven. 12 juil. 2013) $";
  optr->fctptr = OP_Genere_constant_flt;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

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

  /* unit */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_STRING;

  /* X */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.nom";
  optr->Arg_Car[3].unite = "$Arg3";
  optr->Arg_Car[3].famille = "\"auto\"";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name = " \"constante\" ";
  optr->Arg_Car[3].en_name = " \"constant\" ";

}
