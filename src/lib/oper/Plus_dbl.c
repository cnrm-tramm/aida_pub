/****************************************************
*
* OPERATOR       Plus_dbl.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes Arg1 + Arg 2
*
* DESCRIPTION    0peration arithmetique "+"
*
* VERSION        1.0
*
* ARGUMENTS    IN   double  input_1    Any          first value
*              IN   double  input_2    same as 1    second value
*              IN   string  name_out                Name of the result
*              IN   string  en_name_out             English name of the result
*
*              OUT  double  output   same as 1 and 2   Result
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
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* La fonction de calcul */

void
Plus_dbl (unsigned long NLoop, const double *input_1,	/* en ... any */
	  const double *input_2,	/* en ... any  */
	  double *output)
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

int
OP_Plus_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "Plus_dbl, %lu echant., creation de %s (\"%s\")",
		  NbVal, (char *) ArgList[2], (char *) ArgList[3]);

  Plus_dbl (NbVal,
	    (double *) ArgList[0], (double *) ArgList[1],
	    (double *) ArgList[4]);
  return OP_OK;
}

void
ID_Plus_dbl (oper * optr)
{
  strcpy (optr->Nom, "Plus_dbl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Plus_dbl;
  optr->NbArg = 5;		/* doit rester inf. a FIL_MAX_ARG */

  /* input_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* input_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* name_out      */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */

  /* en_name_out      */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */

  /* output */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name = "$Arg3";
  optr->Arg_Car[4].en_name = "$Arg4";
  optr->Arg_Car[4].misval = "$Arg1.misval";

}
