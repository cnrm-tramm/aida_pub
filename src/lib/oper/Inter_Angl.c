/****************************************************
*
* OPERATOR       Inter_Angl.c   FUNCTION  ANSI-C
*
* PURPOSE        Interpolation of a time serie
*
* DESCRIPTION    Routine d'interpolation lineaire, pour variables "float". 
*                et "angulaires" (en RADIANS).
*                schema temporel retenu : 
*                  Variable origine      |       |       |       | 
*                  Variable Destination  | | | | | | | | | | | | | | | | 
*                C'est a dire que la Premiere valeur interpollee correspond a 
*                la premiere valeur d'origine, et les "N" dernieres valeurs 
*                interpollees sont "inventees" apres la derniere valeur 
*                d'origine. 
*                  Dans une version future, on gerera l'argument "decal", 
*               variant entre 0 et N et indiquant a quelle valeur interpollee
*               correspond la premiere valeur d'origine.
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   float  Var_in     radian     Original data
*            IN   float  RapFreq    whithout   frequency ratio 
*            IN   int    Decal      sec/freq   delay between first values
*            OUT  float  Var_out    same as 1  Inter_Anglpolated data
*
* REFERENCES
*
* CHANGES        1.1 Based on standard Inter operator
*
* COPYRIGHT      Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

/* La vraie fonction... */

int
Inter_Angl (unsigned long Nloop,
	    float *Var_in,
	    int RapFreq,
	    int Decal,
	    float *Var_out)

{
  unsigned long i;
  register double X0, X1;
  int j;

  if (Nloop == 0)
    return 0;

  if (RapFreq < 1.0)
    return -1;

  if ((Decal < -RapFreq) || (Decal > RapFreq))
    return -2;

  /* Les cas généraux.... */

  for (i = 0; i < Nloop - 1; i++)
    {
      X0 = Var_in[i];
      X1 = Var_in[i + 1];
      if (fabs (X0 - X1) > M_PI)	/* Warn !! RADIAN only !! */
	{
	  if (X1 < X0)
	    X1 += 2.0 * M_PI;
	  else
	    X1 -= 2.0 * M_PI;
	}
      for (j = 0; j < RapFreq; j++)
	{
	  *Var_out = ((RapFreq - j) * X0 + j * X1) / RapFreq;
	  Var_out++;
	}
    }

  /* Le cas particulier de la derniére second */

  for (j = 0; j < RapFreq; j++)
    {
      *Var_out = Var_in[Nloop - 1];
      Var_out++;
    }

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Inter_Angl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_Inter_Angl (%lu,...);", NbVal);

  CodRet = Inter_Angl (NbVal,
		       (float *) ArgList[0],
		       *((int *) ArgList[1]),
		       *((int *) ArgList[2]),
		       (float *) ArgList[3]);

  switch (CodRet)
    {
    case 0:
      strcat (DiagExec, " OK.");
      return OP_OK;
    case -1:
      strcat (DiagExec, "ERR : Rapport des Freq. < 1.0");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "ERR : Decal trop grand (abs(decal) > RapFreq)");
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }
}

void
ID_Inter_Angl (oper * optr)
{
  strcpy (optr->Nom, "Inter_Angl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Inter_Angl;
  optr->NbArg = 4;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "radian";
  optr->Arg_Car[0].famille = "any";

  /* RapFreq */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "without";

  /* Decal */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "any";	/* count si on est strict */

  /* Var_out */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample * $Arg2";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
