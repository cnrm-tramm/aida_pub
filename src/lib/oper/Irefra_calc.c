/*******************************************************************
* OPERATOR      Irefra_calc.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de la refractivite a partir de
* 		parametres thermodynamiques de base
*
* DESCRIPTION   N s'exprime en fonction de la temperature "T", de la 
*		pression "P", et de la tension de vapeur saturante "e"
*		par la formule : N = 77.604*(P-e)/T + 64.79*e/T + 3.776e5*e/T^2
*		(Baby et al., 1988 )
*		 
* VERSION       1.0
*
* ARGUMENTS     
*               IN      float   Ps	pression statique (hPa) 
*               IN      float   Ts      temperature statique (K or Celsius)
*		IN	float   r	rapport de melange (g/kg) 
*
*               OUT 	float   Irefra	refractivite 
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
#define _XOPEN_SOURCE_EXTENDED
/* Le #define _HPUX_SOURCE n'est la que pour "voir" isfinite sur HPUX_11 */
#define _HPUX_SOURCE

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif
#ifndef K_Ra
#define K_Ra (8.314510 / 0.028964)
#endif
#ifndef K_Rv
#define K_Rv (461.51)
#endif
#define T_EN_C 0
#define T_EN_K 1
#define MANQUANTES 3

int
Irefra_calc (unsigned long ndata,
	     float *Ps,
	     float *Ts,
	     float *r,
	     float *Irefra)

{
  unsigned long i;
  int flag_info;
  double C1 = 77.604;
  double C2 = 64.79;
  double C3 = 3.776e05;

  double CtoK, Ra_sur_Rv;
  double T, P, e, rapm;

  Ra_sur_Rv = K_Ra / K_Rv;

/*** conversion de la tempe. Celsius en Kelvin ***/

  for (i = ndata / 2; i < ndata; i++)
    {
      if (!isfinite (Ts[i]))
	continue;
      else
	{
	  fprintf (stderr, "Ts[i]=%f\n", Ts[i]);
	  if (Ts[i] < 100.)
	    {
	      CtoK = K_T0;
	      flag_info = T_EN_C;
	    }
	  else
	    {
	      CtoK = 0.;
	      flag_info = T_EN_K;
	    }
	  break;
	}
    }
  if (i == ndata - 1)
    {
      /* la moitié du vecteur est en données manquantes */
      flag_info = MANQUANTES;
      return (flag_info);
    }
  for (i = 0; i < ndata; i++)
    {
      if (!isfinite (Ts[i]) || !isfinite (Ps[i]))
	{
	  Irefra[i] = K_NaN;
	  continue;
	}
      T = ((double) Ts[i]) + CtoK;
      P = ((double) Ps[i]);
      rapm = ((double) r[i]) * 0.001;

/*** tension de vapeur (hPa) ***/
      e = (P * rapm) / (Ra_sur_Rv + rapm);

/*** Refractivite ***/
/* attention : P et e en hPa dans la formule */

      Irefra[i] = (float) (C1 * ((P - e) / T) + C2 * (e / T) + C3 * (e / (T * T)));

    }

  return (flag_info);
}

/* fonction d'enrobage */

int
OP_Irefra_calc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = Irefra_calc (Nbval,
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
      strcat (DiagExec, "; Tempé reconnue en °K.");
      break;
    default:
      strcat (DiagExec, "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_Irefra_calc (oper * optr)
{
  strcpy (optr->Nom, "Irefra_calc");
  optr->Version = "1.0";
  optr->Date = "03/25/96";
  optr->fctptr = OP_Irefra_calc;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "gram/kg";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].misval = "$Arg2.misval";
}
