/****************************************************
*
* OPERATOR       PressAltiOACI.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes pressure as a function of altitude following 1993 OACI standard
*
* DESCRIPTION    computes pressure as a function of(altitude) in standard OACI atmosphere model.
*
* VERSION        $Revision: 2017/12/21 $
*
* ARGUMENTS   IN  float altitude  values (m)
              				
*             OUT float pression values (hPa)
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   Manuel de l'atmosphere type OACI troisieme edition 1993 (doc 7488/3)
*
* CHANGES              
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "unit_def.h"

unsigned long int
PressAltiOACI (unsigned long NLoop, float *altitude, float *pression)
{
  unsigned long i;
  unsigned long int nknan;
  const double g_zero = 9.80665;	/* acceleration normalisee de la pesanteur */
  const double r = 6356766.0;	/* rayon terrestre fictif */
  const double R = 287.05287;	/* constante massique des gaz parfaits pour l'air */

  double beta, h, H, Hb, Pb, Tb, P, T;

  /*printf ("__debut__"); */
  for (i = 0; i < NLoop; i++)
    {
      h = altitude[i];		/*altitude geographique */
      H = r * h / (r + h);	/*altitude geopotentielle */

      if ((H < -5000.0) || (!isfinite (H)) || (H > 20000.0))	/*si altitude_geopotentielle <-5000.0, non finie, ou > 20000m */
	{
	  pression[i] = K_NaN;
	  nknan = nknan + 1;
	  continue;
	}

      if ((H > -5000.0) && (H <= 11000.0))	/*si altitude_geopotentielle */
	{
	  if (H <= 0.0)
	    {
	      beta = -0.0065;
	      Hb = -5000.0;	/*altitude geopotentielle de la base du segment */
	      Tb = 320.650;	/*Temperature de la base du segment */
	      Pb = 1776.87;	/*Pression de la base du segment */
	    }
	  else
	    {
	      beta = -0.0065;
	      Hb = 0.0;		/*altitude geopotentielle de la base du segment */
	      Tb = 288.15;	/*Temperature de la base du segment */
	      Pb = 1013.25;	/*Pression de la base du segment */
	    }
	  P = Pb * powf (1.0 + (beta / Tb) * (H - Hb), -g_zero / (beta * R));
	  /*printf("h: %f ,H: %f ,P:%f \n",h,H,P); */
	}

      else
	{
	  Hb = 11000.0;		/*altitude geopotentielle de la base du segment */
	  Pb = 226.32;		/*Pression de la base du segment */
	  T = 216.65;		/*Temperature constante sur l ensemble du segment */
	  P = Pb * exp ((-g_zero * (H - Hb)) / (R * T));
	  /*printf("h: %f ,H: %f ,P:%f \n",h,H,P); */
	}

      pression[i] = P;
    }

  return nknan;
}


int
OP_PressAltiOACI (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CR;

  CR = PressAltiOACI (NbVal, (float *) ArgList[0], (float *) ArgList[1]);


  (void) sprintf (DiagExec, "nb valeurs invalides: %d echant.", CR);

  return OP_OK;
}

void
ID_PressAltiOACI (oper * optr)
{
  int idx;
  strcpy (optr->Nom, "PressAltiOACI");
  optr->Version = "$Revision: 4985 $";
  optr->Date = "$Date: 2012-12-21 16:23:18 +0100 (ven. 21 déc. 2012) $";
  optr->fctptr = OP_PressAltiOACI;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 2;		/* doit rester inf. a FIL_MAX_ARG */
  idx = 0;

  /* altitude */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "m";
  idx = idx + 1;

  /* pression */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "hPa";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].name = "\"Pression OACI a partir de \" + $Arg1.name ";
  optr->Arg_Car[idx].en_name =
    "\"ICAO pressure from \" + $Arg1.english_name ";
  idx = idx + 1;

}
