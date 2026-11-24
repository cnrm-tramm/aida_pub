/******************************************************************
*
* OPERATOR      RapM_Hu.c   ANSI-C
*
* PURPOSE       Compute WaterVapour mixing ratio, given relative humidity
*
* DESCRIPTION   Just a call to the "thermo" library. The formula are :
*                  e = ew(Ts) * Hum / 100.0;
*                  rapm = 622. * e / (Ps - e)
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Hu        %                 Relative Humidity
*              IN   float  Ts        Kelvin or Celsius Static Temperature
*              IN   float  Ps        hPa               Static Pressure
*              OUT  float  RapM      g/Kg              mixing ratio
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "thermo.h"
#include "unit.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif
#define T_UNKNOWN (-1)
#define T_EN_C 0
#define T_EN_K 1
#define MANQUANTES 3

/* La vraie fonction... */
int
RapM_Hu (unsigned long NLoop,
	 const float *Hu,
	 const float *Ts,
	 const float *Ps,
	 float *RapM)
{
  unsigned long i;
  int flag_info;
  float CtoK, TsK;

  flag_info = T_UNKNOWN;

  /* Détermination automatique Kelvin/Celsius */
  flag_info = auto_tempe_unit (NLoop, Ts, &CtoK);

  if (flag_info == MANQUANTES )
    {
      /* la moitié du vecteur est en données manquantes */
      return flag_info;
    }

  for (i = 0; i < NLoop; i++)
    {
      /*if (i % 100000 == 0)
         fprintf (stderr, "--- Ts[%lu]=%f\n", i, Ts[i]); */
      if (!isfinite (Ts[i]) || !isfinite (Ps[i]) || !isfinite (Hu[i])
	  || (Ts[i] < -100.) || (Ps[i] < 0.) || (Hu[i] < 0.))
	{
	  RapM[i] = K_NaN;
	  continue;
	}
      TsK = Ts[i] + CtoK;
      /* On fait appel a la fonction de notre librairie thermo.. */
      rmel_Hu (Hu[i], TsK, Ps[i], &RapM[i]);
    }
  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_RapM_Hu (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "RapM_Hu (%lu ech.), ", NbVal);

  CodRet = RapM_Hu (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2], 
		    (float *) ArgList[3]);

  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case T_EN_K:
      strcat (DiagExec, "; Tempé reconnue en K.");
      break;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; BUG!! Code retour inattendu.");
      return OP_FAIL;
    }

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_RapM_Hu (oper * optr)
{
  strcpy (optr->Nom, "RapM_Hu");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_RapM_Hu;
  optr->NbArg = 4;
  optr->misval_auto = 1;

  /* Hu */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "%";

  /* Ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* Ps */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  /* RapM */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "gram/kg";
  optr->Arg_Car[3].misval = "$Arg2.misval";
  optr->Arg_Car[3].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[3].name = "\"Rapport de melange a partir de \" + $Arg1.name";
  optr->Arg_Car[3].en_name =
    "\"Water vapour mixing ratio from \" + $Arg1.english_name";
}
