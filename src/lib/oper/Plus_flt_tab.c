/****************************************************
*
* OPERATOR       Plus_flt_tab.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes Arg1 + Arg 2
*
* DESCRIPTION    operation arithmetique "+"
*                Cette version sait travailler sur des tableaux.
*
* VERSION        1.0
*
* ARGUMENTS    IN   float  input_1    Any             first value
*              IN   float  input_2    Any             second value
*              IN   int    d_1        Any             Dimension of operand
*              IN   string name_out                Name of the result
*              IN   string en_name_out             English name of the result
*
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
* CHANGES               
*                
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
#include "struct_oper.h"

#include "Plus.h"

int
Plus_tab (unsigned long NLoop, const float *input_1,	/* en ... any */
	 const float *input_2,	/* en ... any  */
	 int d_t, float *output)
{
  unsigned long i;
  int j;

  for (i = 0; i < NLoop; i++)
    {
      for (j = 0; j < d_t; j++)
	{
	  if (!isfinite (*input_1) || !isfinite (*input_2))
	    *output = K_NaN;
	  else
	    *output = (*input_1) + (*input_2);

	  input_1++;
	  input_2++;
	  output++;
	}
    }

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Plus_flt_tab (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;


  (void) sprintf (DiagExec, "Plus_flt_tab, %lu echant., creation de %s (\"%s\")",
		  NbVal, (char *) ArgList[3], (char *) ArgList[4]);

  CodRet = Plus_tab (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    *((int *) ArgList[2]), (float *) ArgList[5]);

  if (CodRet == 0)
    return OP_OK;
  else
    return OP_FAIL;
}

void
ID_Plus_flt_tab (oper * optr)
{
  strcpy (optr->Nom, "Plus_flt_tab");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Plus_flt_tab;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  /* input_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* input_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

    /*  d_1  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "";
  optr->Arg_Car[2].type_sample = "";
  optr->Arg_Car[2].sample = "";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].famille = "";

  /* name_out      */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  /* en_name_out      */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_STRING;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  /* output */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].bornes = "$Arg1.bornes";
  optr->Arg_Car[5].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].name = "$Arg4";
  optr->Arg_Car[5].en_name = "$Arg5";
  optr->Arg_Car[5].misval = "$Arg1.misval";

}
