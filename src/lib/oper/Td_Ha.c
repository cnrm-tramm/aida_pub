/*******************************************************************
* OPERATOR      Td_Ha.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du Point de rosée à partir de l'humidite absolue (g/m3) 
*
* DESCRIPTION     Ha = e / (Rv . T) (Dalton et Gaz Parfait)
*               et e = ew(Td)
*                  Td = inv_ew_Bolton (Ha Rv T)
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   Td	Température du point de rosée (Celsius)
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"
#include "thermo.h"

unsigned long
Td_Ha (unsigned long ndata, const float *Ha, const float *Ts, float *Td)
{
  unsigned long i;
  unsigned long nb_hors_gamme;

  /* Rv, Cste spécifique de la vapeur d'eau, en J / (K*kg)  (= R/Mv) */
  double Rv = 461.51;

  float Ts_to_K;
  float Ts_K, Td_K, e, rhov;

/*** conversion de la tempe. Celsius en Kelvin ***/

  if (Ts[ndata / 2] < 100.)
    Ts_to_K = 273.15;
  else
    Ts_to_K = 0.;

  nb_hors_gamme = 0;
  for (i = 0; i < ndata; i++)
    {
      Ts_K = Ts[i] + Ts_to_K;
      if (Ts_K < 100.)		/* Hors-gamme */
	{
	  Td[i] = K_NaN;
	  nb_hors_gamme++;
	  continue;
	}

      if (Ha[i] < 0.)		/* Hors-gamme */
	{
	  Td[i] = K_NaN;
	  nb_hors_gamme++;
	  continue;
	}
      rhov = Ha[i] / 1000.0;	/* Conversion g/m3 -> kg/m3     */

      e = rhov * Rv * Ts_K;
      /* appel de la fonction inverse de ew() */
      inv_ew_Bolton (e, &Td_K);

      Td[i] = Td_K - 273.15;	/* Conversion en Celsius  */
    }

  return nb_hors_gamme;
}

/* fonction d'enrobage */

int
OP_Td_Ha (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet = Td_Ha (Nbval,
				(float *) ArgList[0],
				(float *) ArgList[1],
				(float *) ArgList[2]);

  if (CodRet == 0)
    {
      DiagExec[0] = 0;
    }
  else
    {
      sprintf (DiagExec, "%lu valeurs hors-gamme (sur %lu)", CodRet, Nbval);
    }
  return OP_OK;
}

void
ID_Td_Ha (oper * optr)
{
  strcpy (optr->Nom, "Td_Ha");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Td_Ha;
  optr->NbArg = 3;

  /* Ha */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/m3";

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
  optr->Arg_Car[2].famille = "auto";
  optr->Arg_Car[2].name = "\"T. du Pt de rosee calculee a partir de \" + $Arg1.name";
  optr->Arg_Car[2].en_name = "\"Dew-point temperature\"";
}
