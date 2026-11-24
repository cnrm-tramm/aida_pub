/****************************************************
*
* OPERATOR       HumCarb.c   FUNCTION  ANSI-C
*
* PURPOSE        Computation of relative Humidity from "Carbon probe"
*
* DESCRIPTION    Calcul de l'humidite a partir de la tension de la 
*                sonde carbone, suivant 3 relations differentes en 
*                fonction de la temperature  (seuils -10 et +12).
*                Puis application d'une correction de vitesse.
*
* VERSION        1.4
*
* ARGUMENTS  IN   float  hum_volt   Volt    Mesure
*            IN   float  tempe      Kelvin  Tempe Air.
*            IN   float  temp_imp   Kelvin  Tempe d'impact
*            IN   float  ps         hPa     Pression statique
*            IN   float  delta_p    hPa     Surpression dynamique
*            IN   float  Coeff1[]           Coeffs pour 1ere gamme (inf -10C)
*            IN   float  Coeff2[]           Coeffs pour 2eme gamme (interm.)
*            IN   float  Coeff3[]           Coeffs pour 3eme gamme (sup +12C)
*            OUT  float  *huc       %       Humidit≈ relative.
*
* ENTRY            
*                 
* SUBPROGRAMS    ew : calcul de la tension de vapeur saturante
*
* FILES   
*
* REFERENCES   
*
* CHANGES        1.3   adapted to changes in categorie's definition
*                1.2   corrected strdup use in inform. function (ID_HumCarb)
*
* COPYRIGHT        Meteo-France
*
* AGREEMENT        The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1


#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif

int
HumCarb (unsigned long NLoop,
	 const float *hum_volt,	/* en ... Volts */
	 const float *tempe,	/* en Kelvin  */
	 const float *temp_imp,	/* en Kelvin  */
	 const float *ps,	/* Pression statique */
	 const float *delta_p,	/* comme son nom l'indique.. */
	 const float Coeff1[],	/* Coeffs pour 1ere gamme (inf -10C) */
	 const float Coeff2[],	/* Coeffs pour 2eme gamme (interm.)  */
	 const float Coeff3[],	/* Coeffs pour 3eme gamme (sup +12C) */
	 float *huc)
{
  unsigned long i;
  float ewt, ewti, corhuc;
  float T_imp, T_stat;

  for (i = 0; i < NLoop; i++)
    {
/*--------------- Correction de temperature ------------------------*/

      if (*tempe < 100)
	T_stat = *tempe + K_T0;
      else
	T_stat = *tempe;

      if (*temp_imp < 100)
	T_imp = *temp_imp + K_T0;
      else
	T_imp = *temp_imp;

      if (T_stat > K_T0 + 12.0)
	{			/* Nous parlons en KELVINs  */
	  *huc = Coeff3[0] + *hum_volt *
	    (Coeff3[1] + *hum_volt *
	     (Coeff3[2] + *hum_volt *
	      (Coeff3[3] + *hum_volt * Coeff3[4])));
	}
      else if (T_stat < K_T0-10.0)
	{			/* toujours KELVINs... */
	  *huc = Coeff1[0] + *hum_volt *
	    (Coeff1[1] + *hum_volt *
	     (Coeff1[2] + *hum_volt *
	      (Coeff1[3] + *hum_volt * Coeff1[4])));
	}
      else
	{			/*  K_T0-10.0 <= tempe =< K_T0+12.0  */
	  *huc = Coeff2[0] + *hum_volt *
	    (Coeff2[1] + *hum_volt *
	     (Coeff2[2] + *hum_volt *
	      (Coeff2[3] + *hum_volt * Coeff2[4])));
	}

/*----------- Correction de vitesse -------------------------------------*/
/*--- Calcul du coefficient de correction Us/Ui=ps*ew(Ti)/pt*ew(T)  ---*/

      if (T_stat < K_T0 )
	{			/* Tempe en Kelvins... Seuil en Kelvins */
	  ewi (T_imp, &ewti);
	  ewi (T_stat, &ewt);
	}
      else
	{
	  ew (T_imp, &ewti);
	  ew (T_stat, &ewt);
	}

      corhuc = *ps * ewti / ((*ps + *delta_p) * ewt);
      *huc = (*huc) * corhuc;

      /* On verifie quand meme que la donnee est valide              */
      /*  Principe :                                                 */
      /*  Si hum hors bornes, on la fixe a une valeur "speciale" :   */
      /*     101 pour > 100,   et 0 pour < 1                         */

      if (*huc > 100.0)
	*huc = 101.0;
      else if (*huc < 1.0)
	*huc = 0.0;

      hum_volt++;
      tempe++;
      temp_imp++;
      ps++;
      delta_p++;
      huc++;
    }
  return 0;
}




/* la fonction d'enrobage classique */

int
OP_HumCarb (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  float Coeff_gam1[5];
  float Coeff_gam2[5];
  float Coeff_gam3[5];

  sprintf (DiagExec, "OP_HumCarb, NbVal=%lu\n", NbVal);

  /* Petite "tricherie" :  */
  /*   comme on ne sait pas encore recevoir des tableaux de     */
  /* constantes depuis le pgm principal, on ne recoit rien ...  */
  /* ... et on passe a la fonctions des valeurs codees "en dur" */
  Coeff_gam1[0] = -30.50129;
  Coeff_gam1[1] = 77.17525;
  Coeff_gam1[2] = -22.24484;
  Coeff_gam1[3] = 2.090671;
  Coeff_gam1[4] = -0.04469137;

  Coeff_gam2[0] = -39.53521;
  Coeff_gam2[1] = 92.50540;
  Coeff_gam2[2] = -29.87445;
  Coeff_gam2[3] = 3.971139;
  Coeff_gam2[4] = -0.1277728;

  Coeff_gam3[0] = -47.03611;
  Coeff_gam3[1] = 102.3352;
  Coeff_gam3[2] = -32.1231;
  Coeff_gam3[3] = 3.971139;
  Coeff_gam3[4] = -0.08768707;

  CodRet = HumCarb (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
		    (float *) ArgList[3],
		    (float *) ArgList[4],
		    Coeff_gam1,
		    Coeff_gam2,
		    Coeff_gam3,
		    (float *) ArgList[5]);
  return OP_OK;
}

void
ID_HumCarb (oper * optr)
{
  strcpy (optr->Nom, "HumCarb");
  optr->Version = "1.4";
  optr->Date = "08/26/96";
  optr->fctptr = OP_HumCarb;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "volt";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "K";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "K";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "hPa";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "hPa";


  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "%";

  /* Et on aimerait pouvoir dire  :      */
  /*  Arg_Car[5].inval = "101"  */
  /* Pour l'instant, on nen peut pas...  */

}
