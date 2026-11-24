/****************************************************
*
* OPERATOR      Calc_Static_RH_From_Dynamic_RH_V1.c   FUNCTION  ANSI-C
*
* PURPOSE       Corrects dynamical effect on RH measurement.
*
* DESCRIPTION   Corrects compression and heating effect when
*               measuring relative humidity on a mobile platform.
*               This program is a faithful transcription in C
*               of a Pascal program which has been communicated
*               by Dr M. Helten (Research centre Juelich GmbH),
*               on Friday, 21 Jul 2000.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Dynamic_RH %          raw measurement.
*             IN   float  tempe      Kelvin     Static Air temperature
*             IN   float  temp_imp   Kelvin     Impact Air temperature
*
*             OUT  float  Static_RH  %          Static humidity
*
* REFERENCES   Dr. M. Helten and Sonntag (1982) 
*
* CHANGES       
*
* AUTHOR       Original not known (Dr. M. Helten ?). C coding by B. Piguet.
*
* COPYRIGHT    Original author and Meteo-France/CNRM
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

/*    Les vraies fonctions....  */

const float _Temp_Triple_H2O_Celsius = 0.01;	/* (Degrees Celsius) */
const float _Temp_Triple_H2O = 273.16;
const float _SpecifiHeat_Cp_Air = 1005;	/* (J/kg,K) */
const float _SpecifiHeat_Cv_Air = 717;	/* (J/kg,K) */
/* const float _Ratio_Cp_Cv_Air = _SpecifiHeat_Cp_Air / _SpecifiHeat_Cv_Air;*/
const float _Ratio_Cp_Cv_Air = 1005. / 717.;

/**
 * @param Temperature [expressed in Kelvins]
 * @param Mode Water Vapor Pressure with regard to :
 *   - 1 >>>> Liquid Water
 *   - 2 >>>> Ice
 *
 * @return Water Vapor Pressure in N/m2 = Pa
 *
 * Formula's source : Sonntag (1982) : Formula 3.17 & 3.18
 *                    with regards to Liquid Water and Ice
 *                    respectivily.
 *
 */
float
Water_Vapor_Pressure_Moz_V1 (float Temperature, int Mode)
{
  const float _A_W = -6094.4342;
  const float _B_W = 21.1249952;
  const float _C_W = -2.7245552E-2;
  const float _D_W = 1.6853396E-5;
  const float _E_W = 2.4575506;

  const float _A_I = -5504.4088;
  const float _B_I = -3.5704628;
  const float _C_I = -1.7337458E-2;
  const float _D_I = 6.5204209E-6;
  const float _E_I = 6.1295027;

  double T_Act, P_H2O;
  double A, B, C, D, E;

  T_Act = Temperature;
  switch (Mode)
    {
    case 1:			/* Over Liquid Water */
      A = _A_W;
      B = _B_W;
      C = _C_W;
      D = _D_W;
      E = _E_W;
      break;
    case 2:			/* Over Ice (T<273.16) */
      if (T_Act >= (_Temp_Triple_H2O))
	{
	  A = _A_W;
	  B = _B_W;
	  C = _C_W;
	  D = _D_W;
	  E = _E_W;
	}
      else
	{
	  A = _A_I;
	  B = _B_I;
	  C = _C_I;
	  D = _D_I;
	  E = _E_I;
	}
      break;
    default:
      A = C = D = E = 0;
      B = 1;
    }				/* End of switch/case. */

  T_Act -= _Temp_Triple_H2O_Celsius;
  /* When translating from Pascal to C, the name of logarithm function
   * changed : "log()" in C is natural logarithm, and thus corresponds 
   * to "Ln()" in Pascal.  */
  P_H2O = A / T_Act + B + C * T_Act + D * (T_Act * T_Act) + E * log (T_Act);
  P_H2O = exp (P_H2O);
  return P_H2O;
}

float
Adiabatic_Heating_Effect_RHD_Over_Liquid_Water (float SAT, float TRT)
{
  const int _EW_Mode = 1;
  float EW_TRT, EW_SAT;

  EW_TRT = Water_Vapor_Pressure_Moz_V1 (TRT, _EW_Mode);
  EW_SAT = Water_Vapor_Pressure_Moz_V1 (SAT, _EW_Mode);

  return EW_TRT / EW_SAT;
}

float
Adiabatic_Compression_Effect_RHD (float SAT, float TRT)
{
  const float _Gamma = _Ratio_Cp_Cv_Air;
  const float _Exponent = _Gamma / (_Gamma - 1);

  return pow (SAT / TRT, _Exponent);
}

void
Calc_Static_RH_From_Dynamic_RH_V1 (const unsigned long NLoop,
				   const float *Dynamic_RH,
				   const float *Static_Air_Temperature,
				   const float *Total_Recovery_Temperature,
				   float *Static_RH,
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

      *Static_RH = Overal_Factor * *Dynamic_RH;

      Static_Air_Temperature++;
      Total_Recovery_Temperature++;
      Dynamic_RH++;
      Static_RH++;
    }
  return;
}

int
OP_Calc_Static_RH_From_Dynamic_RH_V1 (unsigned long NbVal, void *ArgList[],
				      char *DiagExec)
{
  int flag_info_Ts;
  int flag_info_Tt;

  sprintf (DiagExec, "OP_Calc_Static_RH_From_Dynamic_RH_V1 (%lu, ..)", NbVal);

  Calc_Static_RH_From_Dynamic_RH_V1 (NbVal, (float *) ArgList[0],	/* Psc */
				     (float *) ArgList[1],
				     (float *) ArgList[2],
				     (float *) ArgList[3],
				     &flag_info_Ts, &flag_info_Tt);
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
ID_Calc_Static_RH_From_Dynamic_RH_V1 (oper * optr)
{
  strcpy (optr->Nom, "Calc_Static_RH_From_Dynamic_RH_V1");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Calc_Static_RH_From_Dynamic_RH_V1;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* Dynamic_RH */
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

  /* Static_RH */
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
  optr->Arg_Car[3].name = " \"Hum. rel. statique a partir de \" + $Arg1.name";
  optr->Arg_Car[3].en_name =
    " \"Static rel. hum. from \" + $Arg1.english_name";
}
