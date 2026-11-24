/****************************************************
*
* OPERATOR       Reg_lin.c   FUNCTION  ANSI-C
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include <math.h>


void
Reg_lin (unsigned long NLoop,
	 const float *X,
	 const float *Y, double *a, double *b, double *r2, float *Yestim)
{
  unsigned long i;

  double somX, somX2, somXY, somY, somY2;
  double dn, ectypX, ectypY, dx, dy;
  double da, db, dr2;

  somX = 0.;
  somX2 = 0.;
  somXY = 0.;
  somY = 0.;
  somY2 = 0.;
  dn = 0.;

  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (X[i]) || !isfinite (Y[i]))
	continue;

      dx = (double) X[i];
      dy = (double) Y[i];

      somX = somX + dx;
      somX2 = somX2 + dx * dx;

      somY = somY + dy;
      somY2 = somY2 + dy * dy;

      somXY = somXY + dx * dy;
      dn++;
    }


  /*dn = (double)NLoop; */

  ectypX = (somX2 / dn) - (somX / dn) * (somX / dn);
  ectypY = (somY2 / dn) - (somY / dn) * (somY / dn);
  fprintf (stderr, " ectypX = %g , ectypY = %g \n", ectypX, ectypY);

  if (ectypX <= 0.)
    ectypX = 0.;
  else
    ectypX = sqrt (ectypX);


  if (ectypY <= 0.)
    ectypY = 0.;
  else
    ectypY = sqrt (ectypY);

  fprintf (stderr, " ectypX =%g , ectypY= %g \n", ectypX, ectypY);

  if ((ectypX == 0.) || (ectypY == 0.))
    {
      da = 0.;
      db = 0.;
      dr2 = 0.;
    }
  else
    {
      da = (dn * somXY - somX * somY) / (dn * somX2 - somX * somX);
      /*db = (somY/dn) - da * (somX/dn);   */
      db = (somY - da * somX) / dn;
      dr2 = da * da * (dn * somX2 - somX * somX) / (dn * ectypX * ectypY);
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

  *a = (float) da;
  *b = (float) db;
  *r2 = (float) dr2;

  return;
}


/* la fonction d'enrobage classique */

int
OP_Reg_lin (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  double a, b, r2;
  int NCar;

  NCar = sprintf (DiagExec, "Reg_lin : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  Reg_lin (NbVal,
	   (float *) ArgList[0],
	   (float *) ArgList[1], &a, &b, &r2, (float *) ArgList[2]);


  (void) sprintf (DiagExec, "Regression : a = %g b = %g r2=%g \n", a, b, r2);


  return OP_OK;
}

void
ID_Reg_lin (oper * optr)
{
  strcpy (optr->Nom, "Reg_lin");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Reg_lin;
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
  optr->Arg_Car[2].name = "";
  optr->Arg_Car[2].en_name = "";

}
