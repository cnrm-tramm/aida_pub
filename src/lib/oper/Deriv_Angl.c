/****************************************************
*
* OPERATOR      Deriv_Angl.c   FUNCTION  ANSI-C
*
* PURPOSE       Derivate a time serie of an angle 
*
* DESCRIPTION   Calcule la derivee d'une variable "float"
*		et "angulaire" en radians.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  X		radians     	Original data
*             IN   double Freq		Hz   		frequency
*             OUT  float  derivX    	radians/s  	Interpolated data
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

double
Deriv_Angl (unsigned long NbVal, float *X, double freq, float *derivX)
{
  unsigned long i;
  register double X0, X1;
  double dt;

  if (freq <= 0.)
    return -1;

  dt = 1. / ((double) freq);

  /* calcul de la 1ere valeur */

  X0 = (double) X[0];
  X1 = (double) X[1];
  if (fabs (X0 - X1) > M_PI)	/* Warn !! RADIAN only !! */
    {
      if (X1 < X0)
	X1 += 2.0 * M_PI;
      else
	X1 -= 2.0 * M_PI;
    }

  derivX[0] = (X1 - X0) / dt;

  /* boucle */

  for (i = 1; i < NbVal - 1; i++)
    {
      X0 = (double) X[i - 1];
      X1 = (double) X[i + 1];
      if (fabs (X0 - X1) > M_PI)	/* Warn !! RADIAN only !! */
	{
	  if (X1 < X0)
	    X1 += 2.0 * M_PI;
	  else
	    X1 -= 2.0 * M_PI;
	}

      derivX[i] = (X1 - X0) / (2. * dt);
    }

  /* calcul de la derniere valeur */
  X0 = (double) X[NbVal - 2];
  X1 = (double) X[NbVal - 1];
  if (fabs (X0 - X1) > M_PI)	/* Warn !! RADIAN only !! */
    {
      if (X1 < X0)
	X1 += 2.0 * M_PI;
      else
	X1 -= 2.0 * M_PI;
    }

  derivX[NbVal - 1] = (X1 - X0) / dt;

  return dt;
}

/* la fonction d'enrobage classique */

int
OP_Deriv_Angl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  double CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Deriv_Angl (%lu ech), freq=%g", NbVal,
		  *((double *) ArgList[1]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Deriv_Angl (NbVal,
		       (float *) ArgList[0],
		       *((double *) ArgList[1]), (float *) ArgList[2]);

  if (CodRet > 0)
    {
      sprintf (DiagExec, ", dt=%g", CodRet);
      return OP_OK;
    }
  else
    {
      return OP_FAIL;
    }

}

void
ID_Deriv_Angl (oper * optr)
{
  strcpy (optr->Nom, "Deriv_Angl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Deriv_Angl;
  optr->NbArg = 3;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "radians";
  optr->Arg_Car[0].famille = "any";

  /* freq */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* derivX */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit s-1";
  optr->Arg_Car[2].famille = "\"vitesse\"";
  optr->Arg_Car[2].name =
    "\"derivee de \" + $Arg1.name + \" par rapport au temps\"";
  optr->Arg_Car[2].en_name = "\"time derivative of \" + $Arg1.english_name ";
}
