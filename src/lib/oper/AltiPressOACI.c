/****************************************************
*
* OPERATOR       AltiPressOACI.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes altitude as a function of pressure following 1993 OACI standard
*
* DESCRIPTION    computes altitude as a function of(pressure) in standard OACI atmosphere model.
*
* VERSION        $Revision: 2017/12/21 $
*
* ARGUMENTS   IN  float  pression values (hPa)              				
*             OUT float  altitude_geopotentielle values (m)				
*             OUT float  altitude values (m)
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

unsigned long
AltiPressOACI (unsigned long NLoop, float *pression,
	       float *altitude_geopotentielle, float *altitude)
{
  unsigned long i;
  unsigned long nknan;
  const double g = 9.80665;	/* acceleration normalisee de la pesanteur */
  const double R_etoile = 8314.32;	/* constante universelle des gaz */
  const double M_zero = 28.964420;	/*masse molaire moyenne de l'air au niveau de la mer */
  const double r = 6356766.0;	/* rayon terrestre fictif r */

  const double p_moins_5000 = 1776.87;	/*pression_altitude_geopotentielle_moins_5000 */
  const double p_zero = 1013.25;	/*pression_altitude_geopotentielle_zero */
  const double p_11000 = 226.320;	/*pression_altitude_geopotentielle_11000 */
  const double p_20000 = 54.7487;	/*pression_altitude_geopotentielle_20000 */
  double p, H, Hb, Tb, pb, beta;

  nknan = 0;
  for (i = 0; i < NLoop; i++)
    {
      p = pression[i];
      if ((p > p_moins_5000) || (!isfinite (p)) || (p < p_20000))
	/*pression superieure a celle de l'altitude geopotentielle -5000m,  non finiei, ou 
	   inferieure a celle a 20000 m */
	{
	  altitude[i] = K_NaN;
	  nknan = nknan + 1;
	  continue;
	}

      if ((p >= p_11000) && (p < p_moins_5000))	/*pression superieure a celle de l'altitude geopotentielle 0m inferieure a 20000 */
	{
	  if (p >= p_zero)
	    {
	      beta = -0.0065;
	      Hb = -5000.0;
	      Tb = 320.65;	/*temperature pour altitude_geopotentielle_moins_5000 */
	      pb = 1776.87;	/*pression pour altitude_geopotentielle_moins_5000 */
	    }
	  else
	    {
	      beta = -0.0065;
	      Hb = 0.0;
	      Tb = 288.15;	/*temperature pour altitude_geopotentielle_zero */
	      pb = 1013.25;	/*pression pour altitude_geopotentielle_zero */
	    }
	  H = (powf ((p / pb), (-beta) * (R_etoile / M_zero) / g) -
	       1.0) * (Tb / (beta)) + Hb;
	  altitude_geopotentielle[i] = H;

	}

      else if (p >= p_20000)	/*pression superieure a celle de l'altitude geopotentielle 20000m */
	{
	  Hb = 11000.0;
	  Tb = 216.65;		/*temperature pour altitude_geopotentielle_11000 */
	  pb = 226.320;		/*pression pour altitude_geopotentielle_11000 */
	  H = Hb - (R_etoile / M_zero) * Tb / g * log (p / pb);
	  altitude_geopotentielle[i] = H;

	}

      altitude[i] =
	(r * altitude_geopotentielle[i]) / (r - altitude_geopotentielle[i]);
    }

  return nknan;
}

/* la fonction d'enrobage classique */


int
OP_AltiPressOACI (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CR;

  CR =
    AltiPressOACI (NbVal, (float *) ArgList[0], (float *) ArgList[1],
		   (float *) ArgList[2]);


  (void) sprintf (DiagExec, "nb valeurs invalides: %ld echant.", CR);

  return OP_OK;
}

void
ID_AltiPressOACI (oper * optr)
{
  int idx;
  strcpy (optr->Nom, "AltiPressOACI");
  optr->Version = "$Revision: 4985 $";
  optr->Date = "$Date: 2012-12-21 16:23:18 +0100 (ven. 21 déc. 2012) $";
  optr->fctptr = OP_AltiPressOACI;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */
  idx = 0;

  /* pression */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx = idx + 1;

  /* altitude geopotentielle */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "m";       /* pourquoi pas "mgp" ? */
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].name =
    "\"Altitude geopotentielle OACI a partir de \" + $Arg1.name ";
  optr->Arg_Car[idx].en_name =
    "\"ICAO geopotential altitude from \" + $Arg1.english_name ";
  idx = idx + 1;

  /* altitude geometrique */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "m";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].name = "\"Altitude OACI a partir de \" + $Arg1.name ";
  optr->Arg_Car[idx].en_name =
    "\"ICAO altitude from \" + $Arg1.english_name ";
  idx = idx + 1;
} 
