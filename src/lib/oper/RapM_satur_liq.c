/******************************************************************
*
* OPERATOR      RapM_satur_liq.c   ANSI-C
*
* PURPOSE       Compute saturation WaterVapour mixing ratio (over
*           liquid water), given ambiant temperature and pressure.
*
* DESCRIPTION   Just a call to the "thermo" library. The formula are :
*                  e = ew(Ts) 
*                  rapm = 622. * e / (Ps - e)
*                  622 correspond au rapport des masse molaires 
*                  de la vapeur d'eau et de l'air sec (Mv/Ma), multiplié
*                  par 1000 pour obtenir un résultat en g/kg.
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Ts        Kelvin or Celsius Static Temperature
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
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "thermo.h"

#include "unit_def.h"

int
RapM_satur_liq (unsigned long NLoop,
		const float *Ts, const float *Ps, float *RapM)
{
  unsigned long i;
  int flag_info;
  float CtoK, TsK;

  flag_info = auto_tempe_unit (NLoop, Ts, &CtoK);
  if (flag_info == MANQUANTES)
    {
      return flag_info;
    }

  for (i = 0; i < NLoop; i++)
    {
      /*if (i % 100000 == 0)
         fprintf (stderr, "--- Ts[%lu]=%f\n", i, Ts[i]); */
      TsK = Ts[i] + CtoK;
      if (!isfinite (Ts[i]) || !isfinite (Ps[i])
	  || (TsK < 173.) || (Ps[i] < 1.))
	{
	  RapM[i] = K_NaN;
	  continue;
	}
      /* On fait appel a la fonction de notre librairie thermo.. */
      rmel_Hu (100.0, TsK, Ps[i], &RapM[i]);
    }
  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_RapM_satur_liq (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "RapM_satur_liq (%lu ech.) :", NbVal);

  CodRet = RapM_satur_liq (NbVal,
			   (float *) ArgList[0],
			   (float *) ArgList[1], (float *) ArgList[2]);

  strcat (DiagExec, unit_raconte (CodRet));
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_RapM_satur_liq (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "RapM_satur_liq");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_RapM_satur_liq;
  optr->NbArg = 3;
  optr->misval_auto = 1;

  /* Ts */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "Celsius";

  /* Ps */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";

  /* RapM_satur */
  idx++;
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "$Arg2.misval";
  optr->Arg_Car[idx].unite = "gram/kg";
  optr->Arg_Car[idx].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[idx].name =
    " \"Rapport de melange saturant au-dessus eau liquide\" ";
  optr->Arg_Car[idx].en_name =
    " \"Saturation water vapour mixing ratio over liquid water\" ";
}
