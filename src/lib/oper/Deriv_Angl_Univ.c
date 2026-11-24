/****************************************************
*
* OPERATOR      Deriv_Angl_Univ.c   FUNCTION  ANSI-C
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
*             IN   string unite                         angle unit
*             OUT  float  derivX    	radians/s  	Interpolated data
*
* REFERENCES
*
* CHANGES     modified version of Deriv_Angl_Univ.c, independant
*                 of the input unit of the angle  
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>

#include "struct_oper.h"
#include "unit_def.h"
#include "unit.h"

/* La vraie fonction... */

long
Deriv_Angl_Univ (unsigned long NbVal,
		 float *X, double freq, const char *unite, float *derivX)
{
  unsigned long i;
  register double X0, X1;
  double D_to_R = 0;
  double dt;
  int Flag_unit;

  Flag_unit = reconnait_deg_rad (unite);
  switch (Flag_unit)
    {
    case UNIT_IS_DEGREE:
      D_to_R = M_PI / 180.0;
      break;
    case UNIT_IS_RADIAN:
      D_to_R = 1.0;
      break;
    }

  if (freq == 0.)
    return -2;

  dt = 1. / freq;

  fprintf (stderr, "dt = %g\n", dt);

/* calcul de la 1ere valeur */

  X0 = (double) X[0] * D_to_R;
  X1 = (double) X[1] * D_to_R;
  if (fabs (X0 - X1) > M_PI)
    {
      if (X1 < X0)
	X1 += 2.0 * M_PI;
      else
	X1 -= 2.0 * M_PI;
    }

  derivX[0] = (X1 - X0) / (dt * D_to_R);

/* boucle */

  for (i = 1; i < NbVal - 1; i++)
    {
      X0 = (double) X[i - 1] * D_to_R;
      X1 = (double) X[i + 1] * D_to_R;
      if (fabs (X0 - X1) > M_PI)
	{
	  if (X1 < X0)
	    X1 += 2.0 * M_PI;
	  else
	    X1 -= 2.0 * M_PI;
	}

      derivX[i] = (X1 - X0) / (2. * dt * D_to_R);
    }

/* calcul de la derniere valeur */

  X0 = (double) X[NbVal - 2] * D_to_R;
  X1 = (double) X[NbVal - 1] * D_to_R;
  if (fabs (X0 - X1) > M_PI)
    {
      if (X1 < X0)
	X1 += 2.0 * M_PI;
      else
	X1 -= 2.0 * M_PI;
    }

  derivX[NbVal - 1] = (X1 - X0) / (dt * D_to_R);

  return Flag_unit;
}

/* la fonction d'enrobage classique */

int
OP_Deriv_Angl_Univ (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec,
		  "Deriv_Angl_Univ, NbVal=%lu, Freq=%g, Unite=%s",
		  NbVal, *((double *) ArgList[1]), (char *) ArgList[2]);

  CodRet = Deriv_Angl_Univ (NbVal,
			    (float *) ArgList[0],
			    *((double *) ArgList[1]),
			    (char *) ArgList[2], (float *) ArgList[3]);

  switch (CodRet)
    {
    case UNIT_IS_DEGREE:
      strcat (DiagExec, " Unite angle reconnue : degree");
      return OP_OK;
    case UNIT_IS_RADIAN:
      strcat (DiagExec, " Unite angle reconnue : radian");
      return OP_OK;
    case UNIT_IS_UNKNOWN:
      strcat (DiagExec, "ERR : Unite angle non reconnue");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "ERR : Frequence nulle");
      return OP_FAIL;
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_Deriv_Angl_Univ (oper * optr)
{
  strcpy (optr->Nom, "Deriv_Angl_Univ");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Deriv_Angl_Univ;
  optr->NbArg = 4;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Freq */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "Hz";

  /* unite */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";

  /* DerivX */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit s-1 ";
  optr->Arg_Car[3].famille = "$Arg1.famille";	/* Pas toujours vrai ! */
  optr->Arg_Car[3].name = "\"Derivée de \"+ $Arg1.name";
  optr->Arg_Car[3].en_name = "\"Time derivative of\"+$Arg1.english_name";
}
