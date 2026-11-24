/*******************************************************************
* OPERATOR      Ha_Td.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de l'humidite absolue (g/m3) à partir 
*               du point de rosée (°C ou K).
*
* DESCRIPTION     Ha = e / (Rv . T) (Dalton et Gaz Parfait)
*
*               et e = ew(Td)
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   Td	Température du point de rosée
*               IN      float   Ts      temperature statique (K or Celsius)
*
*               OUT     float   Ha	Humidite absolue (g/m3)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    NONE  
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <string.h>

#include "struct_oper.h"
#include "unit_def.h"
#include "thermo.h"

int
Ha_Td (unsigned long ndata, const float *Td, const float *Ts, float Rv,
       float *Ha)
{
  unsigned long i;

  float Ts_to_K, Td_to_K;
  float Ts_K, Td_K, e;
  int flag_info_Ts, flag_info_Td;

  /*** conversion de la tempe. Celsius en Kelvin ***/
  flag_info_Ts = auto_tempe_unit (ndata, Ts, &Ts_to_K);
  flag_info_Td = auto_tempe_unit (ndata, Td, &Td_to_K);

  for (i = 0; i < ndata; i++)
    {
      Ts_K = Ts[i] + Ts_to_K;
      Td_K = Td[i] + Td_to_K;

      if (Ts_K <= 150.)
	{
	  Ha[i] = K_NaN;
	  continue;
	}

      if (Td_K >= 273.15)
	{
	  ew (Td_K, &e);
	}
      else
	{
	  ewi (Td_K, &e);
	}

      /* Les fonctions de la lib. thermo renvoie e en hPa,
       *  la formule nécessite des Pascals */
      Ha[i] = 100.0 * e / (Rv * Ts_K);

      Ha[i] *= 1000.0;		/* Conversion kg/m3 -> g/m3     */

      /* Dernière protection contre les erreurs de mesure. */
      if (Ha[i] < 0.0)
	Ha[i] = 0;
    }

  return flag_info_Td;
}

/* fonction d'enrobage */

int
OP_Ha_Td (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  /* Rv, Cste spécifique de la vapeur d'eau, en J / (K*kg)  (= R/Mv) */
  double Rv = 461.51;
  int CodRet;

  CodRet = Ha_Td (Nbval,
		  (float *) ArgList[0],
		  (float *) ArgList[1], Rv, (float *) ArgList[2]);

  if (CodRet == T_EN_C)
    strcpy (DiagExec, "Td reconnu en °C");
  else
    strcpy (DiagExec, "Td reconnu en K");


  return OP_OK;
}

void
ID_Ha_Td (oper * optr)
{
  strcpy (optr->Nom, "Ha_Td");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ha_Td;
  optr->NbArg = 3;

  /* Td */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "Celsius";

  /* T */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Celsius";

  /* Ha */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "gram/m3";
  optr->Arg_Car[2].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[2].name =
    " \"Humidite absolue a partir de \"  + $Arg1.name + \" et \" +  $Arg2.name ";
  optr->Arg_Car[2].en_name =
    " \"absolute humidity from \" + $Arg1.english_name  + \" and \" +  $Arg2.english_name ";
}
