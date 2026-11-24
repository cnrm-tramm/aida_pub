/****************************************************
*
* OPERATOR      Dynamic_RH_from_static.c   FUNCTION  ANSI-C
*
* PURPOSE       Simulates dynamical effect on RH measurement.
*
* DESCRIPTION   Compute compression and heating effect when
*               measuring relative humidity on a mobile platform.
*               This program is the reciprocal of Calc_Static_RH_From_Dynamic_RH_V1

*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Static_RH  %          Static measurement.
*             IN   float  tempe      Kelvin     Static Air temperature
*             IN   float  temp_imp   Kelvin     Impact Air temperature
*
*             OUT  float  Dynamic_RH %          Computed Dynamic humidity
*
* REFERENCES   Dr. M. Helten and Sonntag (1982) 
*
* CHANGES       
*
* AUTHOR       B. Piguet.
*
* COPYRIGHT    Meteo-France/CNRM
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"
#include "unit.h"

#include "Calc_Static_RH_From_Dynamic_RH_V1.h"

void
Dynamic_RH_from_static (const unsigned long NLoop,
			const float *Static_RH,
			const float *Static_Air_Temperature,
			const float *Total_Recovery_Temperature,
			float *Dynamic_RH,
			int *flag_info_Ts, int *flag_info_Tt)
{
  float CtoK_S;			/* Pour la conversion C->K de T_Stat */
  float CtoK_T;			/* Pour la conversion C->K de T_Tot  */

  float Clausius_Factor;
  float Compression_Factor;
  float Overal_Factor;
  unsigned long i;

  /* Détermination automatique Kelvin/Celsius */
  *flag_info_Ts = auto_tempe_unit (NLoop, Static_Air_Temperature, &CtoK_S);
  *flag_info_Tt =
    auto_tempe_unit (NLoop, Total_Recovery_Temperature, &CtoK_T);

  for (i = 0; i < NLoop; i++)
    {
      Clausius_Factor =
	Adiabatic_Heating_Effect_RHD_Over_Liquid_Water
	(*Static_Air_Temperature + CtoK_S,
	 *Total_Recovery_Temperature + CtoK_T);

      Compression_Factor =
	Adiabatic_Compression_Effect_RHD (*Static_Air_Temperature + CtoK_S,
					  *Total_Recovery_Temperature +
					  CtoK_T);

      Overal_Factor = Clausius_Factor * Compression_Factor;

      *Dynamic_RH = *Static_RH / Overal_Factor;

      Static_Air_Temperature++;
      Total_Recovery_Temperature++;
      Dynamic_RH++;
      Static_RH++;
    }
  return;
}

int
OP_Dynamic_RH_from_static (unsigned long NbVal, void *ArgList[],
			   char *DiagExec)
{
  int flag_info_Ts;
  int flag_info_Tt;

  sprintf (DiagExec, "OP_Dynamic_RH_from_static (%lu, ..)", NbVal);

  Dynamic_RH_from_static (NbVal, (float *) ArgList[0],	/* Psc */
			  (float *) ArgList[1],
			  (float *) ArgList[2],
			  (float *) ArgList[3], &flag_info_Ts, &flag_info_Tt);
  if (flag_info_Ts)
    strcat (DiagExec, "; Ts reconnue en K");
  else
    strcat (DiagExec, "; Ts reconnue en °C");

  if (flag_info_Tt)
    strcat (DiagExec, "; Tt reconnue en K");
  else
    strcat (DiagExec, "; Tt reconnue en °C");


  return OP_OK;
}

void
ID_Dynamic_RH_from_static (oper * optr)
{
  strcpy (optr->Nom, "Dynamic_RH_from_static");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Dynamic_RH_from_static;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* Static_RH */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "%";

  /* Static_Air_Temperature */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "K";

  /* Total_recovery_Temperature */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "K";

  /* Dynamic_RH */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "%";
  optr->Arg_Car[3].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[3].name = " \"Hum. rel. dynamique a partir de \" + $Arg1.name";
  optr->Arg_Car[3].en_name =
    " \"Dynamic rel. hum. from \" + $Arg1.english_name";
}
