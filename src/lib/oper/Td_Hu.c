/*******************************************************************
* OPERATOR      Td_Hu.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du Point de rosée à partir de l'humidite relative (%) 
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
Td_Hu (unsigned long ndata, float *Hu, float *Ts, float *Td)
{
  unsigned long i, nb_too_low;

  float Ts_to_K;
  int flag_info_Ts;
  float Ts_K, Td_K, e, ew;

  /*** conversion de la tempe. Celsius en Kelvin ***/
  flag_info_Ts = auto_tempe_unit (ndata, Ts, &Ts_to_K);

  nb_too_low = 0;
  for (i = 0; i < ndata; i++)
    {
      Ts_K = Ts[i] + Ts_to_K;

      if (Ts_K == 0.)
	{
	  Td[i] = K_NaN;
	  continue;
	}

      /* Au dessus de 100 % , on ramene a 100 % */
      if (Hu[i] > 100.)
	{
	  Hu[i] = 100.;
	}

      ew_Bolton (Ts_K, &ew);    /*  ew en hPa, selon choix Bolton    */

      /* La ligne ci-dessous cache deux termes qui y sont sans y être.
       *  Ami relecteur, saura-tu les trouver ? */
      e = Hu[i] * ew;

      /* Explication : 1 = 100/100.
       * La vraie formule est : e = Hu/100 * ew.
       * mais ew est en hPa, et e doit être en Pa (par définition de la fct inv_ew_Bolton() )
       * donc e = 100 * Hu/100 * ew 
       *      e =  Hu * ew 
       * Etonnant, non ?   */
      inv_ew_Bolton (e, &Td_K);

      Td[i] = Td_K - 273.15;	/* Conversion en Celsius  */
    }

  return flag_info_Ts;
}

/* fonction d'enrobage */

int
OP_Td_Hu (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = Td_Hu (Nbval,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2]);

  if (CodRet == 0)
    strcpy (DiagExec, "T reconnu en °C");
  else
    strcpy (DiagExec, "T reconnu en K");

  return OP_OK;
}

void
ID_Td_Hu (oper * optr)
{
  strcpy (optr->Nom, "Td_Hu");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Td_Hu;
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

  /* Td */
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
    "\"temperature du point de rosee issue de \"+$Arg1.name";
  optr->Arg_Car[2].en_name =
    "\"dew-point temperature from \" + $Arg1.english_name";
}
