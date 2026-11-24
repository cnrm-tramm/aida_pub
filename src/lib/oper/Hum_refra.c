/*******************************************************************
* OPERATOR      Hum_refra.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de l'humidite relative a partir de la 
*		refractivite ( N= 1e6*(n-1) ) de l'air. 
*
* DESCRIPTION   N s'exprime en fonction de la temperature "T", de la 
*		pression "P", et de la tension de vapeur saturante "e"
*		par la formule : N = 77.604*(P-e)/T + 64.79*e/T + 3.776e5*e/T^2
*		(Baby, H.B., P. Golé, and J. Lavergnat (1988) :  "A
*               model for the tropospheric excess path length of radio
*               waves from surface meteorological measurements".
*               Radio Science, Vol. 23, No. 6, pp. 1023-1038.)
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   Irefra	refractivite de l'air 
*               IN      float   Ps	pression statique (hPa) 
*               IN      float   Ts      temperature statique (K or Celsius)
*
*               OUT 	float   Hu	humidite relative (%) 
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "thermo.h"
#include "struct_oper.h"
#include "unit.h"

int
Hum_refra (unsigned long ndata,
	   float *Irefra,
	   float *Ps,
	   float *Ts,
	   float *Hu)
{
  unsigned long i;
  int flag_info;
  double C1 = 77.604;
  double C2 = 64.79;
  double C3 = 3.776e05;
  float CtoK;
  double e, T, P, N;
  
  double ewt;

  float f_T, f_ewt;
  /* fonction de la librairie unit.c pour transformer les °C en K*/
  flag_info  = auto_tempe_unit (ndata,Ts, &CtoK);
  for (i = 0; i < ndata; i++)
    {
      T = ((double)Ts[i]) + (double)CtoK;
      P = (double)Ps[i];
      N = (double)Irefra[i];

/*** tension de vapeur (hPa) ***/
      e = ((N * T) - (C1 * P)) / (C2 - C1 + (C3/T) );
      if (e < 0.)
	e = 0.;

/*** tension de vapeur saturante ew(T) ****/
      
      f_T = (float)T;
      ew (f_T, &f_ewt);
      ewt = (double)f_ewt;
      
      Hu[i] = (float)(100.0 * e / ewt);

    }

  return (flag_info);
}

/* fonction d'enrobage */

int
OP_Hum_refra (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;
  CodRet= Hum_refra (Nbval,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(float *) ArgList[2],
			(float *) ArgList[3]);
   switch (CodRet)
       {
         case 0:
            strcat (DiagExec, "; Tempé reconnue en °C.");
            break;
         case 1:
            strcat (DiagExec, "; Tempé reconnue en K.");
            break;
         default:
            strcat (DiagExec, "; Trop de valeurs manquantes : par défaut température en K.");
            break;
    }
			  

  return OP_OK;
}

void
ID_Hum_refra (oper * optr)
{
  strcpy (optr->Nom, "Hum_refra");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Hum_refra;
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
  optr->Arg_Car[3].unite = "%";
}
