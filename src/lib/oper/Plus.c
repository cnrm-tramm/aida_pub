/****************************************************
*
* OPERATOR       Plus.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes Arg1 + Arg 2
*
* DESCRIPTION    operation arithmetique "+"
*
* VERSION        1.4
*
* ARGUMENTS    IN   float  input_1    Any             first value
*              IN   float  input_2    Any             second value
*              OUT  float  output   same as 1 and 2   Result
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES        1.3  Adapted to new def. of categorie in Arg_profil       
*                1.2  corrected use of strdup in inform. function (ID_Plus)
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>

void
Plus (unsigned long NLoop,
      const float *input_1,	/* en ... any */
      const float *input_2,	/* en ... any  */
      float *output)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *output = *input_1 + *input_2;

      input_1++;
      input_2++;
      output++;
    }
}


/* la fonction d'enrobage classique */
#include "struct_oper.h"

int
OP_Plus (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "Plus, %lu echant.", NbVal);

  Plus (NbVal,
        (float *) ArgList[0], (float *) ArgList[1], (float *) ArgList[2]);
  return OP_OK;
}

void
ID_Plus (oper * optr)
{
  strcpy (optr->Nom, "Plus");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Plus;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */
  optr->repl_oper = "Plus_flt";
  optr->repl_cause = "Ne permet pas de fixer les champs \"name\" du vecteur produit";


  /* input_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* input_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* output */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].name =
    "\"Somme de \" + $Arg1.name + \" et \" + $Arg2.name ";
  optr->Arg_Car[2].en_name =
    "\"Sum of \" + $Arg1.english_name + \" and \" + $Arg2.english_name ";
}
