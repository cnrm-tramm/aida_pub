/*******************************************************************
* OPERATOR      Tdf_Hu.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du de la température du point de rosée ou de
*               givre à partir de l'humidite relative (%) 
*
* DESCRIPTION   Hu = e/ew(T) (tensions en Pa)
*               et e = ew(Td)
*               Td = inv_ew_Bolton(Hu*ew(T))
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   Hu	Humidité relative à l'eau liquide (%)
*               IN      float   Ts      temperature statique (K or Celsius)
*
*               OUT     float   Td	température du point de rosée (Celsius)
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
#include "thermo.h"
#include "unit.h"

int
Tdf_Hu (unsigned long ndata, float *Hu, float *Ts, float *Td)
{
  unsigned long i;
  unsigned long nb_hum_low, nb_hum_high, nb_T_low;

  float Ts_to_K;
  int flag_info_Ts;
  float Ts_K, Td_K, e, ew;

  /*** conversion de la tempe. Celsius en Kelvin ***/
  flag_info_Ts = auto_tempe_unit (ndata, Ts, &Ts_to_K);

  nb_hum_low = 0;
  nb_hum_high = 0;
  nb_T_low = 0;
  for (i = 0; i < ndata; i++)
    {
      Ts_K = Ts[i] + Ts_to_K;

      if (Ts_K <= 10.)
	{
          nb_T_low += 1;
	  Td[i] = K_NaN;
	  continue;
	}

      /* Au dessus de 100 % , on ramene a 100 % */
      if (Hu[i] > 100.)
	{
          nb_hum_high += 1;
	  Hu[i] = 100.;
	}
      else if (Hu[i] < 0.)
	{
          nb_hum_low += 1;
	  Td[i] = K_NaN;
	  continue;
	}

      /* toujours ew (pas ei), par définition OMM de Hu. */
      ew_Bolton (Ts_K, &ew);	/*  ew en hPa, selon choix Bolton    */

      e = Hu[i] / 100.0 * ew;

      /* Td ou Tf, selon la valeur de e.
       *   La limite de 6.11 hPa correspond à la pression du point triple
       * de l'eau : au-dessus, on est dans le domaine des Td (>0),
       * au-dessous, dans celui des Tf (<0)
       */
      if (e > 6.11)
	{
	  /* inv_ew_Bolton a été codé pour des e exprimés en Pa */
	  inv_ew_Bolton (e * 100, &Td_K);
	}
      else
	{
	  inv_ewi_OMM (e, &Td_K);
	}

      /* Conversion en Celsius, qqsoit l'unité de T d'origine  */
      Td[i] = Td_K - 273.15;
    }

  return flag_info_Ts;
}

/* fonction d'enrobage */

int
OP_Tdf_Hu (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = Tdf_Hu (Nbval,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2]);

  strcpy (DiagExec, unit_raconte (CodRet));

  return OP_OK;
}

void
ID_Tdf_Hu (oper * optr)
{
  strcpy (optr->Nom, "Tdf_Hu");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 aoÃ»t 2012) $";
  optr->fctptr = OP_Tdf_Hu;
  optr->NbArg = 3;

  /* Hu */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "%";

  /* T */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Celsius";

  /* Td/Tf */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "Celsius";
  optr->Arg_Car[2].famille = " \"temperature\" ";
  optr->Arg_Car[2].name =
    "\"temperature du point de rosee ou givre correspondant à \"+$Arg1.name";
  optr->Arg_Car[2].en_name =
    "\"dew-point or frost-point temperature from \" + $Arg1.english_name";
}
