/****************************************************
*
* OPERATOR      Deriv_Temps.c   FUNCTION  ANSI-C
*
* PURPOSE       Derivate a time serie  
*
* DESCRIPTION   Calcule la derivee par rapport au temps d'une 
*            variable "float" echantillonnée regulièrement.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  X	       unite     	Original data
*             IN   double Freq		Hz   		frequency
*             OUT  float  derivX    	unite/s  	Interpolated data
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

long
Deriv_Temps (unsigned long NbVal, float *X, double freq, float *derivX)
{
  unsigned long i;
  register double X0, X1;

  if (freq == 0.)
    return -1;

  if (NbVal == 0)
    return 1;

  if (NbVal == 1)
    {
      derivX[0] = K_NaN;
      return 1;
    }

/* calcul de la 1ere valeur */

  X0 = (double) X[0];
  X1 = (double) X[1];

  derivX[0] = (X1 - X0) * freq;

/* boucle */

  for (i = 1; i < NbVal - 1; i++)
    {
      X0 = (double) X[i - 1];
      X1 = (double) X[i + 1];

      derivX[i] = (X1 - X0) * freq / 2.;
    }

/* calcul de la derniere valeur */

  X0 = (double) X[NbVal - 2];
  X1 = (double) X[NbVal - 1];

  derivX[NbVal - 1] = (X1 - X0) * freq;

  return 1;
}

/* la fonction d'enrobage classique */

int
OP_Deriv_Temps (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Deriv_Temps (%lu ech), freq = %g", NbVal,
		  *((double *) ArgList[1]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Deriv_Temps (NbVal,
			(float *) ArgList[0],
			*((double *) ArgList[1]), (float *) ArgList[2]);

  if (CodRet > 0)
    return OP_OK;
  else
    return OP_FAIL;

}

void
ID_Deriv_Temps (oper * optr)
{
  strcpy (optr->Nom, "Deriv_Temps");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Deriv_Temps;
  optr->NbArg = 3;

  /*  X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /*  freq  */
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
  optr->Arg_Car[2].unite = "$Arg1.unit s-1 ";
  optr->Arg_Car[2].famille = "$Arg1.famille";
  optr->Arg_Car[2].name = "\"Derivee temporelle de \"+$Arg1.name";
  optr->Arg_Car[2].en_name =  "\"Time derivative of \"+$Arg1.english_name";
}
