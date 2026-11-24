/****************************************************
*
* OPERATOR       Reg_Pol2.c   FUNCTION  ANSI-C
*
* PURPOSE        Calcule la regression polynomiale 
*		 d'ordre 2 entre X et Y.
*
*
* DESCRIPTION    
*
* VERSION        1.0
 
* ARGUMENTS    IN   float  X               first parameter
*              IN   float  Y               second parametre
*              OUT  float  Yestim          Result ( Yestim=a+b*X+c^2)
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   Calcul des probabilites et statistiques Tome III
*                                            J. Vialar 1977
*
* CHANGES        
*
* COPYRIGHT      Meteo-France
*                CNRM/GMEI/TRAMM
*
* AGREEMENT      The author wishes that it works.
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include <math.h>


void
Determinant (const float mat[10], float *delta)
{
  *delta = mat[1] * (mat[5] * mat[9] - mat[6] * mat[8])
    - mat[2] * (mat[4] * mat[9] - mat[6] * mat[7])
    + mat[3] * (mat[4] * mat[8] - mat[5] * mat[7]);
}


void
Reg_Pol2 (unsigned long NLoop,
	  const float *X,
	  const float *Y, double *a0, double *a1, double *a2, float *Yestim)
{
  double Som_X, Som_X2, Som_X3, Som_X4, Som_Y, Som_XY, Som_X2Y, X_tempo;
  double Mom_X, Mom_X2, Mom_X3, Mom_X4, Mom_Y, Mom_XY, Mom_X2Y, X_courant,
    Y_courant;
  unsigned long N_XY, i;
  float mat[10], delta, det;

/* Quelques initialisations */

  Som_X = 0.;
  Som_X2 = 0.;
  Som_X3 = 0.;
  Som_X4 = 0.;
  Som_XY = 0.;
  Som_Y = 0.;
  Som_X2Y = 0.;
  N_XY = 0;



  for (i = 0; i < NLoop; i++)
    {
      X_courant = X[i];
      Y_courant = Y[i];
      if (isfinite (X_courant) && isfinite (Y_courant))
	{
	  Som_X += X_courant;
	  Som_Y += Y_courant;
	  Som_XY += X_courant * Y_courant;
	  X_tempo = X_courant * X_courant;
	  Som_X2 += X_tempo;
	  Som_X2Y += X_tempo * Y_courant;
	  X_tempo = X_tempo * X_courant;
	  Som_X3 += X_tempo;
	  X_tempo = X_tempo * X_courant;
	  Som_X4 += X_tempo;
	  N_XY += 1;
	}
    }


  if (N_XY == 0)
    {

      Mom_X = 0.0;
      Mom_Y = 0.0;
      Mom_XY = 0.0;
      Mom_X2 = 0.0;
      Mom_X2Y = 0.0;
      Mom_X3 = 0.0;
      Mom_X4 = 0.0;
    }
  else
    {
      Mom_X = Som_X / N_XY;
      Mom_Y = Som_Y / N_XY;
      Mom_XY = Som_XY / N_XY;
      Mom_X2 = Som_X2 / N_XY;
      Mom_X2Y = Som_X2Y / N_XY;
      Mom_X3 = Som_X3 / N_XY;
      Mom_X4 = Som_X4 / N_XY;
    }

  mat[1] = 1;
  mat[2] = Mom_X;
  mat[3] = Mom_X2;
  mat[4] = Mom_X;
  mat[5] = Mom_X2;
  mat[6] = Mom_X3;
  mat[7] = Mom_X2;
  mat[8] = Mom_X3;
  mat[9] = Mom_X4;

  Determinant (mat, &delta);
  det = delta;
/* pas fais le test delta egal zero */

  mat[1] = Mom_Y;
  mat[4] = Mom_XY;
  mat[7] = Mom_X2Y;
  Determinant (mat, &delta);
  *a0 = delta / det;

  mat[1] = 1;
  mat[4] = Mom_X;
  mat[7] = Mom_X2;
  mat[2] = Mom_Y;
  mat[5] = Mom_XY;
  mat[8] = Mom_X2Y;
  Determinant (mat, &delta);
  *a1 = delta / det;

  mat[2] = Mom_X;
  mat[5] = Mom_X2;
  mat[8] = Mom_X3;
  mat[3] = Mom_Y;
  mat[6] = Mom_XY;
  mat[9] = Mom_X2Y;
  Determinant (mat, &delta);
  *a2 = delta / det;


  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (*X))
	{
	  *Yestim = K_NaN;
	  continue;
	}
      *Yestim = (float) (*a0 + *a1 * *X + *a2 * *X * *X);
      Yestim++;
      X++;
    }

  return;
}


/* la fonction d'enrobage classique */

int
OP_Reg_Pol2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  double a0, a1, a2;

  Reg_Pol2 (NbVal,
	    (float *) ArgList[0],
	    (float *) ArgList[1], &a0, &a1, &a2, (float *) ArgList[2]);


  (void) sprintf (DiagExec,
		  "Regression : a0 = %g a1 = %g a2=%g \n", a0, a1, a2);


  return OP_OK;
}


void
ID_Reg_Pol2 (oper * optr)
{
  strcpy (optr->Nom, "Reg_Pol2");
  optr->Version = "1.0";
  optr->Date = "23/10/01";
  optr->fctptr = OP_Reg_Pol2;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].famille = "any";

  /* Yestime Vecteur issue de la regression */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[2].sample = "$Arg2.sample";
  optr->Arg_Car[2].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[2].unite = "$Arg2.unit";
  optr->Arg_Car[2].famille = "$Arg2.famille";
  optr->Arg_Car[2].misval = "$Arg2.misval";

}
