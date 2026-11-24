/*******************************************************************
* OPERATOR	lwckp.c FUNCTION ANSI-C
* 
* PURPOSE 	computation of liquid water content from King-Probe data
*
* DESCRIPTION   Cette fonction calcule le contenu en eau liquide » 
*                partir des donn≈es issues d'une sonde King. 
* 
* VERSION       1.4
*
* ARGUMENTS 	IN 	float 	Pw	total power delivered to
*					the master coil (W)
*	 	
*		IN 	float 	Ta 	static air temperature (K)
*		IN 	float	Ps 	static air pressure (hPa)
*		IN 	float 	Vp	true air speed (m/s)
*		IN 	float 	l 	master coil's length (mm)
*		IN 	float 	d 	master coil's diameter (mm)
*		IN 	float 	Tw 	temperature of the wire (K)
*		IN 	float 	Twh 	temperature which the impacting
*					water evaporates
*		IN 	float 	A	|empiric constant for computing the
*		IN 	float 	X	|dry term 
*		
*		OUT 	float 	LWC  	liquid water content (g/m3)	
*
* ENTRY 	NONE
*
* SUBPROGRAMS	NONE
*
* REFERENCES 	CSIRO-KING
*		Liquid Water Content Probe
*		PMS Model KLWC-5
*		Operating and Servicing Manual
*		Particle Measuring Systems, Inc, Boulder, Colorado
*
* CHANGES       1.3   adapted to changes in categorie's definition
*               1.2   added arg's sampling description in ID_... function
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/MMA
*		42, av. G. Coriolis
*		31057 	TOULOUSE cedex
*
**********************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
lwckp (unsigned long Nloop,
       const float *Pw,
       const float *Ta,
       const float *Ps,
       const float *Vp,
       const float l,
       const float d,
       const float Tw,
       const float Twh,
       const float A,
       const float X,
       float *LWC)
{
  unsigned long i;

  float dens, Pdry, Pwet, CtoK, Tair;

  float Lv = 2.264e6;		/* chaleur latente de l'eau (T=100≥C) */
  float c = 4218;		/* chaleur specifique de l'eau */

/* tempe en Kelvin ou Celsius */

  if (Ta[Nloop / 2] < 100.)
    CtoK = 273.15;
  else
    CtoK = 0.;

  fprintf (stderr, " Constante de conversion degre C en K : %f\n", CtoK);

  for (i = 0; i < Nloop; i++)
    {
      /* Seuil de 3.0 Watt fixÈ arbitrairement et empiriquement */
      /* le 26/2/2001, au vu de donnÈes de CARL-2000 */
      if ((*Vp > 50.) && (*Pw > 3.0))
	{
	  Tair = *Ta + CtoK;
	  dens = *Ps / (2.8705 * Tair);
	  Pdry = A * (Tw - Tair) * pow (*Vp * dens, X);
	  Pwet = l * d * 1e-6 * (*Vp) * (Lv + c * (Twh - Tair));
	  *LWC = 1000. * ((*Pw - Pdry) / Pwet);
	}
      else
	{
	  *LWC = 0.;
	}
      Pw++;
      Ta++;
      Ps++;
      Vp++;
      LWC++;
    }
  return 0;
}

/* fonction d'enrobage */

int
OP_lwckp (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = lwckp (Nbval,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3],
		      *((float *) ArgList[4]),
		      *((float *) ArgList[5]),
		      *((float *) ArgList[6]),
		      *((float *) ArgList[7]),
		      *((float *) ArgList[8]),
		      *((float *) ArgList[9]),
		      (float *) ArgList[10]);


  return OP_OK;
}

void
ID_lwckp (oper * optr)
{
  strcpy (optr->Nom, "lwckp");
  optr->Version = "$Revision$";
  optr->Date = "08/26/96";
  optr->fctptr = OP_lwckp;
  optr->NbArg = 11;

  /* Pw */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "watt";

  /* Ta */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Kelvin";

  /* Ps */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].unite = "hPa";

  /* Vp */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "m/s";

  /* l */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "mm";

  /* d */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "mm";

  /* Tw */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "Kelvin";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "Kelvin";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "none";

  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = NULL;
  optr->Arg_Car[9].sample = NULL;
  optr->Arg_Car[9].unite = "none";

  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  /* Pour le futur...  */
  /* optr->Arg_Car[10].misval = "-99"; */
  optr->Arg_Car[10].unite = "gram/m3";
  /*** SB correction famille ***/
  optr->Arg_Car[10].famille = "\"eau_liquide\"";
  optr->Arg_Car[10].name = " \"Contenu en eau liquide issu du King-Probe\" ";
  optr->Arg_Car[10].en_name = " \"Liquid water content from King Probe\" ";

}
