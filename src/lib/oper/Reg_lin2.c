/****************************************************
*
* OPERATOR       Reg_lin2.c   FUNCTION  ANSI-C
*
* PURPOSE        Calcule la regression lineaire au sens
*		 des moindres carres entre les parametres 
* 		 X et Y.
*
*
* DESCRIPTION    
*
* VERSION        $Revision$
*
* ARGUMENTS    IN   float  X               first parameter
*              IN   float  Y               second parametre
*              OUT  float  Yestim          Result ( Yestim  = A.X + b )
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include <math.h>


void
Reg_lin2 (unsigned long NLoop,
	  const float *X,
	  const float *Y, double *a, double *b, double *r2, float *Yestim)
{
  unsigned long i;

  double somX, somY;
  double MomX, MomX2, MomXY, MomY, MomY2;
  double dn, ectypX, ectypY, dx, dy;
  double da, db, dr2;
  unsigned long n, n2;

  somX = 0.;
  somY = 0.;
  MomX = 0.;
  MomX2 = 0.;
  MomXY = 0.;
  MomY = 0.;
  MomY2 = 0.;

  n = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (X[i]) || !isfinite (Y[i]))
	continue;

      somX = somX + (double) X[i];
      somY = somY + (double) Y[i];

      n++;
    }
  dn = n;
  MomX = somX / dn;
  MomY = somY / dn;

  n2 = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (X[i]) || !isfinite (Y[i]))
	continue;

      dx = (double) X[i] - MomX;
      dy = (double) Y[i] - MomY;
      MomX2 = MomX2 + dx * dx;
      MomY2 = MomY2 + dy * dy;
      MomXY = MomXY + dx * dy;

      n2++;
    }

  if (n != n2)
    {
      fprintf (stderr, "%s\n",
	       "Erreur nb ech pour moy != nb ech pour mom 2 !!!!");
    }

  MomX2 = MomX2 / dn;
  MomY2 = MomY2 / dn;
  MomXY = MomXY / dn;

  /* fprintf (stderr,
     " SomX = %g , SomY = %g , MomX2= %g , MomY2= %g, MomXY= %g,dn= %g \n",
     somX, somY, MomX2, MomY2, MomXY, dn); */

  if (MomX2 <= 0.)
    ectypX = 0.;
  else
    ectypX = sqrt (MomX2);

  if (MomY2 <= 0.)
    ectypY = 0.;
  else
    ectypY = sqrt (MomY2);

  /* fprintf (stderr, " ectypX = %g , ectypY = %g \n", ectypX, ectypY); */

  if ((ectypX == 0.) || (ectypY == 0.))
    {
      da = 0.;
      db = 0.;
      dr2 = 0.;
    }
  else
    {
      /* da = (MomXY - MomX * MomY) / (MomX2 - MomX * MomX); */
      da = MomXY / MomX2;
      /* db = MomY - da * MomX; */
      db = MomY - da * MomX;
      /* dr2 = (MomXY - MomX * MomY) / (ectypX * ectypY); */
      dr2 = MomXY / (ectypX * ectypY);
    }

  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (X[i]))
	{
	  Yestim[i] = K_NaN;
	  continue;
	}
      dx = (double) X[i];
      Yestim[i] = (float) (da * dx + db);
    }

  *a = da;
  *b = db;
  *r2 = dr2;

  return;
}


/* la fonction d'enrobage classique */

int
OP_Reg_lin2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  double a, b, r2;

  (void) sprintf (DiagExec, "Reg_lin2, Nb_ech=%lu", NbVal);

  Reg_lin2 (NbVal,
	    (float *) ArgList[0],
	    (float *) ArgList[1], &a, &b, &r2, (float *) ArgList[2]);

  (void) sprintf (DiagExec, "Regression : a = %g b = %g r2=%g \n", a, b, r2);

  return OP_OK;
}

void
ID_Reg_lin2 (oper * optr)
{
  strcpy (optr->Nom, "Reg_lin2");
  optr->Version = "1.4";
  optr->Date = "$Date$";
  optr->fctptr = OP_Reg_lin2;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Y */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].famille = "any";

  /* Yestim */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg2.unit";
  optr->Arg_Car[2].famille = "$Arg2.famille";
  optr->Arg_Car[2].misval = "$Arg2.misval";
  optr->Arg_Car[2].name = "$Arg1.name + \" ajuste sur \" + $Arg2.name";
  optr->Arg_Car[2].en_name =
    "$Arg1.english_name + \" fitted to \" + $Arg2.english_name";
}
