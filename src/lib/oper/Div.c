/****************************************************
*
* OPERATOR       Div.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes Arg1 / Arg 2
*
* DESCRIPTION    operation arithmetique "/" (division)
*
* VERSION        $Revision$
*
* ARGUMENTS    IN   float  input_1    Any              first value
*              IN   float  input_2    Any              second value
*              OUT  float  output    ratio of 1 and 2  Result
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
#define _XOPEN_SOURCE_EXTENDED

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

void
Div (unsigned long NLoop,
     const float *input_1,	/* en ... any */
     const float *input_2,	/* en ... any  */
     float *output)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (*input_1) || !isfinite (*input_2))
	*output = K_NaN;

      else
	*output = (*input_1) / (*input_2);

      input_1++;
      input_2++;
      output++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Div (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "Div, %lu echant.", NbVal);

  Div (NbVal,
       (float *) ArgList[0], (float *) ArgList[1], (float *) ArgList[2]);

  return OP_OK;
}

void
ID_Div (oper * optr)
{
  strcpy (optr->Nom, "Div");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Div;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  /* input_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* input_2 */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* output */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit / ($Arg2.unit)";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].name =
    "\"Rapport de \" + $Arg1.name + \" sur \" + $Arg2.name ";
  optr->Arg_Car[2].en_name =
    "\"Ratio of \" + $Arg1.english_name + \" to \" + $Arg2.english_name ";
}
