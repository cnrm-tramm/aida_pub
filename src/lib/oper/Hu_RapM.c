/******************************************************************
*
* OPERATOR      Hu_RapM.c   ANSI-C
*
* PURPOSE       Compute Relative Humidity, given WaterVapour mixing ratio
*
* DESCRIPTION   Just a call to the "thermo" library. The formula are :
*                  e = P * RapM / ( RapM + 622. )
*                  Hum = 100.0 e/ew(T);
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  RapM     g/Kg               Wat. Vap. mixing ratio
*              IN   float  Ts       Kelvin or Celsius  Static Temperature
*              IN   float  Ps       hPa                Static Pressure
*              OUT  float  Hu       %                  Relative Humidity
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

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "unit_def.h"
#include "thermo.h"

/* La vraie fonction... */
int
Hu_RapM (unsigned long NLoop,
	 const float *RapM,
	 const float *Ts,
	 const float *Ps,
	 float *Hu)
{
  unsigned long i;
  int flag_info;
  float CtoK, TsK;

  flag_info = auto_tempe_unit (NLoop, Ts, &CtoK);
  if (flag_info == MANQUANTES)
    return flag_info;

  for (i = 0; i < NLoop; i++)
    {
      if (i % 100000 == 0)
	fprintf (stderr, "--- Ts[%lu]=%f\n", i, Ts[i]);
      if (!isfinite (Ts[i]) || !isfinite (Ps[i]) || !isfinite (RapM[i]) ||
	  (Ts[i] < -100.) || (Ps[i] < 0.) || (RapM[i] < 0.))
	{
	  Hu[i] = K_NaN;
	  continue;
	}

      TsK = Ts[i] + CtoK;
      /* On fait appel a la fonction de notre librairie thermo.. */
      Hu_rmel (RapM[i], TsK, Ps[i], &(Hu[i]));

      /* Au dessus de 101 % , on tronque */
      if (Hu[i] > 101.)
	{
	  Hu[i] = 101. + Hu[i] * 1.0e-3;
	}

    }
  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_Hu_RapM (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Hu_RapM(%lu ech.) ", NbVal);

  CodRet = Hu_RapM (NbVal,
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
      strcat (DiagExec, "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
    }

  return OP_OK;

}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Hu_RapM (oper * optr)
{
  strcpy (optr->Nom, "Hu_RapM");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Hu_RapM;
  optr->NbArg = 4;
  optr->misval_auto = 1;

  /* RapM */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/kg";

  /* Ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* Ps */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  /* Hu */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "%";
  optr->Arg_Car[3].misval = "$Arg2.misval";
  optr->Arg_Car[3].famille = "\"eau_vapeur\"";
  optr->Arg_Car[3].name = "\"Humidité relative\" ";
  optr->Arg_Car[3].en_name = "\"Relative humidity from \" + $Arg1.english_name ";

}
