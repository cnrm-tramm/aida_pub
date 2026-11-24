/****************************************************
*
* OPERATOR      Inv_PolyCal2.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute the inverse function
*               of a second order polynomial function of "float" variables
*
* DESCRIPTION   Standard calculation...
*
* VERSION       1.5
*
* ARGUMENTS   IN   float  Y    Any          "X" value
*             IN   float  C0         Any          Constant coefficient
*             IN   float  C1         Any          coefficient of X
*             IN   float  C2         Any          coefficient of X^2
*	      IN   float  min                     Minimun of the result
*             IN   float  max                     Maximum of the result
*             OUT  float  X  same as 2      Result
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       1.4   Adapted to new def. of categorie in Arg_profil
*               1.3   gave standard name to ID_Inv_PolyCal2 function
*               1.2   switched args order/added comments
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

/* La vraie fonction... */
int
Inv_PolyCal2 (unsigned long NLoop,
	      const float *Y,
	      float C0, /* Unused  ? */
	      float C1,
	      float C2,
	      float min_X,
	      float max_X,
	      float *X)
{
  unsigned long i;

  double a, b, c, x0, x1, delta;

  a = (double) C2;
  b = (double) C1;

  for (i = 0; i < NLoop; i++)
    {
      c = (double) (C2 - Y[i]);
      delta = b * b - 4. * a * c;

      if (delta < 0.)
	return -1;

      x0 = (-b - sqrt (delta)) / (2. * a);
      x1 = (-b + sqrt (delta)) / (2. * a);

/** choix de la racine avec les bornes min et max */

      if ((x0 > max_X) || (x0 < min_X))
	{
	  if ((x1 > max_X) || (x1 < min_X))
	    return -2;
	  else
	    X[i] = (float) x1;
	}
      else
	{
	  if ((x1 > max_X) || (x1 < min_X))
	    X[i] = (float) x0;
	  else
	    return -3;
	}
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Inv_PolyCal2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec,
		  "Inv_PolyCal2, NbVal=%lu, coefs =[%g, %g, %g], range=[%g, %g]",
		  NbVal,
		  *((float *) ArgList[1]),
		  *((float *) ArgList[2]),
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]),
		  *((float *) ArgList[5]));

  CodRet = Inv_PolyCal2 (NbVal,
			 (float *) ArgList[0],
			 *((float *) ArgList[1]),
			 *((float *) ArgList[2]),
			 *((float *) ArgList[3]),
			 *((float *) ArgList[4]),
			 *((float *) ArgList[5]),
			 (float *) ArgList[6]);

  switch (CodRet)
    {

    case -1:
      {
	sprintf (DiagExec, " ERREUR : Discriminant negatif, pas de solution \n");
	return (OP_FAIL);
      }
    case -2:
      {
	sprintf (DiagExec, " ERREUR : Aucune solution dans les bornes \n");
	return (OP_FAIL);
      }
    case -3:
      {
	sprintf (DiagExec, " ERREUR : 2 solutions dans les bornes, choix impossible \n");
	return (OP_FAIL);
      }
    }

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Inv_PolyCal2 (oper * optr)
{
  strcpy (optr->Nom, "Inv_PolyCal2");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Inv_PolyCal2;
  optr->NbArg = 7;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "unknown";
  optr->Arg_Car[6].famille = "\"auto\"";

}
