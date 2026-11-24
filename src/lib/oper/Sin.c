/****************************************************
*
* OPERATOR       Sin.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes sin(X)
*
* DESCRIPTION    Calls the sin function of the math lib.
*
* VERSION        $Revision: 2013/03/12 $
*
* ARGUMENTS   IN  float  X      value
              IN  string unit   "degre*" or "rad"  unit of the input
*             OUT float  output  sin of X
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
#include "unit_def.h"
#include "unit.h"

int
Sin (unsigned long NLoop, const float *X,	/* ???? en ... any  */
     const char *unit, float *output)
{
  unsigned long i;
  int Flag_unit;

  Flag_unit = reconnait_deg_rad (unit);
  if (Flag_unit == UNIT_IS_UNKNOWN)
    return Flag_unit;

  for (i = 0; i < NLoop; i++)
    {
      if (Flag_unit == UNIT_IS_DEGREE)
	{
	  output[i] = sin (X[i] * M_PI / 180.);
	}
      else
	{
	  output[i] = sin (X[i]);
	}
    }
  return Flag_unit;
}


/* la fonction d'enrobage classique */

int
OP_Sin (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CR;
  (void) sprintf (DiagExec, "Sin, %lu echant., unite de l'argument = %s",
		  NbVal, (char *) ArgList[1]);

  CR = Sin (NbVal, (float *) ArgList[0], (char *) ArgList[1],
	    (float *) ArgList[2]);

  if (CR == UNIT_IS_UNKNOWN)
    return OP_FAIL;

  return OP_OK;
}

void
ID_Sin (oper * optr)
{
  int idx;
  strcpy (optr->Nom, "Sin");
  optr->Version = "$Revision: 4985 $";
  optr->Date = "$Date: 2012-12-21 16:23:18 +0100 (ven. 21 déc. 2012) $";
  optr->fctptr = OP_Sin;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  idx = 0;
  /* X */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* unit */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_STRING;
  optr->Arg_Car[idx].array_dim = "1";
  idx++;

  /* output */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].name = "\"Sinus de \" + $Arg1.name ";
  optr->Arg_Car[idx].en_name = "\"Sinus of \" + $Arg1.english_name ";
  idx++;
}
