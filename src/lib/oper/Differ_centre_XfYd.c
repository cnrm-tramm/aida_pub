/****************************************************
*
* OPERATOR      Differ_centre_XfYd.c   FUNCTION  ANSI-C
*
* PURPOSE       Differenciate a variable with respect to another

* DESCRIPTION   Differenciation numérique d'une
*            variable "float" par rapport à une autre, de type "double".
*
*
* ARGUMENTS   IN   float  X	       unite_1    	Original data
*             IN   double Y	        unite_2   	other data
*             OUT  float  diffc_XY   	unite_1/unite_2	Interpolated data
*
* REFERENCES
*
* CHANGES       
*
* COPTRIGHT     Meteo-France
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

long
Differ_centre_XfYd (unsigned long NbVal, float *X, double *Y, float *diffc_XY)
{
  unsigned long i;
  register double X0, X1;
  register double Y0, Y1;

  if (NbVal == 0)
    return 1;

  if (NbVal == 1)
    {
      diffc_XY[0] = K_NaN;
      return 1;
    }

  /* calcul de la 1ere valeur */
  X0 = (double) X[0];
  X1 = (double) X[1];
  Y0 = (double) Y[0];
  Y1 = (double) Y[1];

  diffc_XY[0] = (X1 - X0) / (Y1 - Y0);

  /* boucle */
  for (i = 1; i < NbVal - 1; i++)
    {
      X0 = (double) X[i - 1];
      X1 = (double) X[i + 1];
      Y0 = (double) Y[i - 1];
      Y1 = (double) Y[i + 1];

      diffc_XY[i] = (X1 - X0) / (Y1 - Y0);
    }

  /* calcul de la derniere valeur */
  X0 = (double) X[NbVal - 2];
  X1 = (double) X[NbVal - 1];
  Y0 = (double) Y[NbVal - 2];
  Y1 = (double) Y[NbVal - 1];

  diffc_XY[NbVal - 1] = (X1 - X0) / (Y1 - Y0);

  return 1;
}

/* la fonction d'enrobage classique */

int
OP_Differ_centre_XfYd (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Differ_centre_XfYd (%lu ech)", NbVal);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Differ_centre_XfYd (NbVal,
			     (float *) ArgList[0],
			     (double *) ArgList[1], (float *) ArgList[2]);

  if (CodRet > 0)
    return OP_OK;
  else
    return OP_FAIL;

}

void
ID_Differ_centre_XfYd (oper * optr)
{
  strcpy (optr->Nom, "Differ_centre_XfYd");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Differ_centre_XfYd;
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

  /*  Y  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* diffc_XY */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit / $Arg2.unit";
  optr->Arg_Car[2].famille = "";
  optr->Arg_Car[2].name =
    "$Arg1.name + \"differencie par rapport a \" + $Arg2.name";
  optr->Arg_Car[2].en_name =
    "\"Derivative of \"+$Arg1.english_name + \" wrt \" + $Arg2.english_name";
}
