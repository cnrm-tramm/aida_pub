/****************************************************
*
* OPERATOR      HumEmpir.c   FUNCTION  ANSI-C
*
* PURPOSE       Applies empirical calibration to a capacitive Humidity probe
*
* DESCRIPTION   
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  tempe      Kelvin     Static Air temperature
*             IN   float  temp_imp   Kelvin     Impact Air temperature
*             IN   float  huca_Volt  Volts      probe measurement.
*             IN   float  ps         hPa        Static Air pressure.
*             IN   float  delta_p    hPa        Static Air pressure.
*             IN   float* C_HuCa                Calibration coefficients
*             OUT  float  huca       %          Computed humidity
*
* REFERENCES    CNRM/CAM
*
* CHANGES       
*
* COPYRIGHT     Meteo-France/CNRM
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif

/*    La vraie fonction....  */

int
HumEmpir (const unsigned long NLoop,
      	  const float *tempe,	/* TEMPE en Kelvins */
	  const float *temp_imp,	/* en Kelvins aussi. */
	  const float *huca_Volt,
	  const float *ps,
	  const float *delta_p,
	  const float C_HuCa[],
	  float *huca)
{

  float huca_cal, ewt, ewti;
  float corhuc;
  float huca_brute;
  unsigned long i;

  /* passage volts en pourcents */
  for (i = 0; i < NLoop; i++)
    {
      if (*huca_Volt < 0.0)
	{
	  *huca = 0.5;
	}
      else if (*huca_Volt > 10.0)
	{
	  *huca = 100.5;
	}
      else
	{
	  /* Les cas "*huca_Volt dans la gamme"   */
	  if (*huca_Volt < C_HuCa[0])
	    {
	      huca_brute = C_HuCa[1] + *huca_Volt * C_HuCa[2];
	    }
	  else
	    {
	      huca_brute = C_HuCa[3] + *huca_Volt * C_HuCa[4];
	    }

/*--------- Correction de temperature -------------------*/

	  /* ATTENTION : la formule donnee par CAM/INS contient "293.16 - TIRT" */
	  /* On suppose qu'il s'agit bien de Kelvins.... */

	  huca_cal = huca_brute + 0.075 * (293.16 - *temp_imp);

/*-------- Correction de vitesse ------------------------*/

	  if (*tempe <= K_T0)
	    {			/* Limite en Kelvins... */
	      ewi (*temp_imp, &ewti);
	      ewi (*tempe, &ewt);
	    }
	  else
	    {
	      ew (*temp_imp, &ewti);
	      ew (*tempe, &ewt);
	    }

	  corhuc = *ps * ewti / ((*ps + *delta_p) * ewt);

	  *huca = huca_cal * corhuc;

	  /* On verifie quand meme que la donnee est valide              */
	  /*  Principe :                                                 */
	  /*  Si hum hors bornes, on la fixe a une valeur "speciale" :   */
	  /*     101 pour hum > 100,   et 0 pour hum < 1                 */

	  if (*huca > 100.0)
	    *huca = 101.0;
	  else if (*huca < 1.0)
	    *huca = 0.0;
	}
      tempe++;
      temp_imp++;
      huca_Volt++;
      ps++;
      delta_p++;
      huca++;
    }
  return 0;
}

int
OP_HumEmpir (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  float C_HuCa[5];

  fprintf (stderr, "OP_HumEmpir, NbVal=%lu\n", NbVal);

  C_HuCa[0] = *((float *) ArgList[5]);
  C_HuCa[1] = *((float *) ArgList[6]);
  C_HuCa[2] = *((float *) ArgList[7]);
  C_HuCa[3] = *((float *) ArgList[8]);
  C_HuCa[4] = *((float *) ArgList[9]);

  CodRet = HumEmpir (NbVal, 
		     (float *) ArgList[0],	/* Psc */
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     (float *) ArgList[3],
		     (float *) ArgList[4], 
		     C_HuCa, 
		     (float *) ArgList[10]);

  return OP_OK;
}

void
ID_HumEmpir (oper * optr)
{
  strcpy (optr->Nom, "HumEmpir");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_HumEmpir;
  optr->NbArg = 11;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "K";

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


  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "without";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "without";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "without";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "without";

  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].type_sample = NULL;
  optr->Arg_Car[9].sample = NULL;
  optr->Arg_Car[9].unite = "without";


  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  /* Formule "fixe" pour la taille :  0.0 + 1.0 * taille (Arg1) */
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].unite = "%";

}
