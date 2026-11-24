/****************************************************
*
* OPERATOR       Div_tab.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes Arg1 / Arg 2
*
* DESCRIPTION    Operation arithmetique "/" (division)
*                Cette version sait travailler sur des tableaux.
*                Si Arg1 et Arg2 sont de même dimension, fait la division terme à terme.
*                Si Arg1 est un tableau et Arg2 un scalaire, tous les éléments de Arg1
*                sont divises par le élément de Arg2.
*
* VERSION        $Revision$
*
* ARGUMENTS    IN   float  input_1    Any             first value
*              IN   int    d_1        Any             Dimension of first operand
*              IN   float  input_2    Any             second value
*              IN   int    d_2        Any             Dimension of second operand
*              OUT  float  output                     Result
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


int
Div_tab (unsigned long NLoop, const float *input_1,	/* en ... any */
	 int d_1, const float *input_2,	/* en ... any  */
	 int d_2, float *output)
{
  unsigned long i;
  int j;

  if ((d_1 <= 0) || (d_2 <= 0))
    return -1;

  if ((d_2 != d_1) && (d_2 != 1))
    return -2;

  for (i = 0; i < NLoop; i++)
    {
      for (j = 0; j < d_1; j++)
	{
	  if (!isfinite (*input_1) || !isfinite (*input_2))
	    *output = K_NaN;
	  else
	    *output = (*input_1) / (*input_2);

	  input_1++;
	  if (d_2 != 1)
	    input_2++;
	  output++;
	}
      if (d_2 == 1)
	input_2++;
    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Div_tab (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec,
		  "Div_tab, NbVal=%lu, Dimension dividance = %d, Dimension diviseur = %d",
		  NbVal,
		  *((int *) ArgList[1]),
		  *((int *) ArgList[3]));

  CodRet = Div_tab (NbVal,
		    (float *) ArgList[0],
		    *((int *) ArgList[1]),
		    (float *) ArgList[2],
		    *((int *) ArgList[3]), (float *) ArgList[4]);

  if (CodRet == 0)
    return OP_OK;
  else
    return OP_FAIL;
}

void
ID_Div_tab (oper * optr)
{
  strcpy (optr->Nom, "Div_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Div_tab;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 5;		/* doit rester inf. a FIL_MAX_ARG */

  /* input_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /*  d_1  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "";
  optr->Arg_Car[1].type_sample = "";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].famille = "";

  /* input_2 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "any";	/* devrait être $Arg1.dim_array OR 1 */
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  /*  d_2  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "";
  optr->Arg_Car[3].type_sample = "";
  optr->Arg_Car[3].sample = "";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].famille = "";

  /* output */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[4].bornes = "$Arg1.bornes";
  optr->Arg_Car[4].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit / ($Arg3.unit)";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  /* optr->Arg_Car[4].famille = "$Arg1.misval";    La division risque-t-elle de changer la famille ? */
  optr->Arg_Car[4].name =
    "\"Rapport de \" + $Arg1.name + \" sur \" + $Arg3.name ";
  optr->Arg_Car[2].en_name =
    "\"Ratio of \" + $Arg1.english_name + \" to \" + $Arg3.english_name ";

}
