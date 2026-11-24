/*******************************************************************
* OPERATOR      ha_irefra.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de l'humidite absolue a partir de la 
*		refractivite ( N= 1e6*(n-1) ) de l'air. 
*
* DESCRIPTION   N s'exprime en fonction de la temperature "T", de la 
*		pression "P", et de la tension de vapeur saturante "e"
*		par la formule : N = 77.604*(P-e)/T + 64.79*e/T + 3.776e5*e/T^2
*		(Baby et al., 1988 )
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   Irefra	refractivite de l'air 
*               IN      float   Ps	pression statique (hPa) 
*               IN      float   Ts      temperature statique (K or Celsius)
*
*               OUT 	float   Ha	humidite absolue (g/m3) 
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    Mesure de l'humidite de l'air avec un refractometer  
*               J-Y. Delahaye, J. Lavergnat
*		CETP, Avril 1994
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
ha_irefra (unsigned long ndata,
	   float *Irefra,
	   float *Ps,
	   float *Ts,
	   float *Ha)
{
  long i;

  double C1 = 77.604;
  double C2 = 64.79;
  double C3 = 3.776e05;
  double R = 287.05;

  double CtoK;
  double e, r, T, P, N;

/*** conversion de la tempe. Celsius en Kelvin ***/
  if (Ts[0] < 100.)
    CtoK = 273.15;
  else
    CtoK = 0.;

  for (i = 0; i < ndata; i++)
    {
      T = ((double) Ts[i]) + CtoK;
      P = (double) Ps[i];
      N = (double) Irefra[i];

/*** tension de vapeur (hPa) ***/
      e = ((N * T) - (C1 * P)) / (C2 - C1 + (C3 / T));
      if (e < 0.)
	e = 0.;

/*** rapport de melange (g/kg) ****/
      r = 622. * (e / (P - e));

/*** rapport de melange en (g/m3) ***/
      Ha[i] = (float) (r * ((P * 100.) / (R * T)));
/*
   fprintf (stderr, " e = %f r = %f P = %f T = %f\n",
   e, r, Ps[i], T);
 */
    }

  return (0);
}

/* fonction d'enrobage */

int
OP_ha_irefra (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = ha_irefra (Nbval,
			  (float *) ArgList[0],
			  (float *) ArgList[1],
			  (float *) ArgList[2],
			  (float *) ArgList[3]);

  return OP_OK;
}

void
ID_ha_irefra (oper * optr)
{
  strcpy (optr->Nom, "ha_irefra");
  optr->Version = "1.0";
  optr->Date = "03/25/96";
  optr->fctptr = OP_ha_irefra;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "gram/m3";
}
