/*********************************************************
* OPERATOR 	Ecrete.c FUNCTION ANSI-C
*
* PURPOSE       Detects period where a input parameter values are 
*		greater than the values of another input parameter
*		It replace the first ones values by the second ones
*
*	        Detecte les passages ou les valeurs d'un parametre en entree
*               sont superieures a celles d'un autre parametre en entree.
*               Remplace ces valeurs par celles du second parametre.
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	param_1	        parameter to correct
*		IN 	float 	unit_1  	first parameter unit
*		IN 	float 	param_1 	compared parameter
*		IN 	float 	unit_2  	second parameter unit
*
*		OUT 	int   	param_out_1     Flag (1 if replacement occured)
*		OUT 	float 	param_out_2     corrected parameter
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <gene.h>

#include "struct_oper.h"
#include "unit.h"

long
Ecrete (unsigned long Nloop,
	const float *param_1,
	char *unit_1,
	const float *param_2,
	char *unit_2,
        int *param_out_1,
        float *param_out_2)
{
  unsigned long i;
  int CodRet;
  double pente = 0.0, intercepte = 0.0;

  /* Les cas bizarres de pointeurs sur rien ... */
  if (unit_1 == NULL)
    {
      (void) fprintf (stderr,
		      "+++ Ecrete : unité du premier paramètre inexistante\n");
      return -1;
    }
  else if (unit_2 == NULL)
    {
      (void) fprintf (stderr,
		      "+++ Ecrete : unité du second paramètre inexistante\n");
      return -2;
    }

  CodRet = unitconvert (unit_1, unit_2, &pente, &intercepte);
  if (CodRet != 0)
    {
      return -3;
    }
  fprintf (stderr, "%f %f\n", pente, intercepte);

  for (i = 0; i < Nloop; i++)
    {
      if ((param_1[i]) > (pente * param_2[i] + intercepte))
	{
	  param_out_1[i] = 1;
	  param_out_2[i] = (pente * param_2[i] + intercepte);
	}
      else
	{
	  param_out_1[i] = 0;
	  param_out_2[i] = param_1[i];
	}
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_Ecrete (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "Ecrete, NbVal=%lu, ", Nbval);

  CodRet = Ecrete (Nbval,
		   (float *) ArgList[0],
		   (char *) ArgList[1],
		   (float *) ArgList[2],
		   (char *) ArgList[3],
		   (int *) ArgList[4], (float *) ArgList[5]);

  if (CodRet >= 0)
    {
      return OP_OK;
    }
  else
    {
      return OP_FAIL;
    }
}

void
ID_Ecrete (oper * optr)
{
  strcpy (optr->Nom, "Ecrete");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ecrete;
  optr->NbArg = 6;

  /*  param_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /*  unit_1  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_STRING;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "any";

  /*  param_2 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";	/*  Compatible avec celle de param_1 */

  /*  unit_2  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[4].unite = "without";
  optr->Arg_Car[4].famille = "\"controle\"";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].name =
    "\"Indicateur de remplacement de \" + $Arg1.name + \" par \" + Arg2.name";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[4].name = "$Arg1.name + \" borne par \" + Arg2.name";
}
