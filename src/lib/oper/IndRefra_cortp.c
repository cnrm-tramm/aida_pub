/*******************************************************************
* OPERATOR      IndRefra_cortp.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de la refractivite N = (n-1)*1e6 a partir de 
*		la mesure du refractometer de J-Y Delahaye.
*
* DESCRIPTION   La refractivite est calcule a partir 
*		de la tension de sortie du refractometer.
*		Une correction de temperature est effectue 
*		pour palier a la derive due a la temperature.
*		(J-Y Delahaye )
*
* VERSION       1.0
*
* ARGUMENTS     IN      float   Vrefra	Output Voltage from the Refractometer (Volt) 
*               IN      float   Tcav  Temperature de la cavite 
*		IN 	float	fr	frequence d'acquisition 
*               IN      float   K       calibration coefficient 
*               IN      float   V0      calibration coefficient 
*               IN      float   KT      calibration coefficient 
*		IN	float 	N00	calibration coefficient
*
*               OUT     float   Irefra  refractivite de l'air 
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	Les formules sont donnees par J-Y Delahaye 
*		Irefra = K*Vrefra -V0 -KT*( Tcav[t+120] - 30 ) + N00
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
IndRefra_cortp (unsigned long ndata,
		float *Vrefra,
		float *Tcav,
		float fr,
		float K,
		float V0,
		float KT,
		float N00,
		float *Irefra)
{
  unsigned long i;
  long decal;

  float KtoC, Tcav_cels;
  float tau = 120.;		/* constante de temps */

  if (Tcav[ndata/2] < 100.)
    KtoC = 0.;
  else
    KtoC = -273.15;

  for (i = 0; i < ndata; i++)
    {
      decal = i - tau * fr;
      if (decal < 0)
	decal = 0;

      Tcav_cels = Tcav[decal] + KtoC;

      Irefra[i] = K * Vrefra[i] - V0 -
	KT * (Tcav_cels - 30.) + N00;


      if (Irefra[i] < 0.)
	Irefra[i] = 0.;
    }

  return (0);
}

/* fonction d'enrobage */

int
OP_IndRefra_cortp (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = IndRefra_cortp (Nbval,
			       (float *) ArgList[0],
			       (float *) ArgList[1],
			       *((float *) ArgList[2]),
			       *((float *) ArgList[3]),
			       *((float *) ArgList[4]),
			       *((float *) ArgList[5]),
			       *((float *) ArgList[6]),
			       (float *) ArgList[7]);

  return OP_OK;
}

void
ID_IndRefra_cortp (oper * optr)
{
  strcpy (optr->Nom, "IndRefra_cortp");
  optr->Version = "1.0";
  optr->Date = "04/02/96";
  optr->fctptr = OP_IndRefra_cortp;
  optr->NbArg = 8;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "Volt";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "without";

}
