/****************************************************
*
* OPERATOR       Atan2.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes atan2(Y, X), ie atan(Y/X), using the sign
*                of the two arguments to determine the quadrant
*
* DESCRIPTION    Calls the atan2 function of the math lib.
*
* VERSION        $Revision$
*
* ARGUMENTS   IN  float  Y      Any              first value
*             IN  float  X      Same unit as Y   second value
              IN  string unit   "degre*" or "rad"  unit of the result
*             OUT float  output                  arc tangent of Y/X
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
Atan2 (unsigned long NLoop, const float *Y,	/* en ... any */
       const float *X,		/* en ... any  */
       const char *unit, float *output)
{
  unsigned long i;
  int Flag_unit;

  Flag_unit = reconnait_deg_rad (unit);
  if (Flag_unit == UNIT_IS_UNKNOWN)
    return Flag_unit;

  for (i = 0; i < NLoop; i++)
    {
      /* Convention pour le couple (0.0, 0.0) */
      if ((Y[i] == 0.0) & (X[i] == 0.0))
	output[i] = 0.0;
      else
	/* Attention a l'ordre particulier des arguments : Y est avant X */
	output[i] = atan2 (Y[i], X[i]);
    }
  if (Flag_unit == UNIT_IS_DEGREE)		/* Si résultat désiré en degrés */
    for (i = 0; i < NLoop; i++)
      {
	output[i] *= 180. / M_PI;
      }
  return Flag_unit;
}


/* la fonction d'enrobage classique */

int
OP_Atan2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CR;

  (void) sprintf (DiagExec, "Atan2, %lu echant., unite du resultat = %s", NbVal,
		  (char *) ArgList[2]);

  CR = Atan2 (NbVal, (float *) ArgList[0], (float *) ArgList[1],
	 (char *) ArgList[2], (float *) ArgList[3]);

  if (CR == UNIT_IS_UNKNOWN)
    return OP_FAIL;

  return OP_OK;
}

void
ID_Atan2 (oper * optr)
{
  strcpy (optr->Nom, "Atan2");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Atan2;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* Y */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* X */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";

  /* unit */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";

  /* output */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg3";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name =
    "\"Arctangente du rapport de \" + $Arg1.name + \" sur \" + $Arg2.name ";
  optr->Arg_Car[3].en_name =
    "\"Principal value of the arc tangent of \" + $Arg1.english_name + \" / \" + $Arg2.english_name ";
}
