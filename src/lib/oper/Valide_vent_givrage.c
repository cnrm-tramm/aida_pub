/*********************************************************
* OPERATOR 	Valide_vent_givrage.c FUNCTION ANSI-C
*
* PURPOSE       
*		
*
*	        Mise a zero des valeurs de derapage et d'incidence lorsque
*               la mesure semble incorrecte (givrage, ...)
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	int	flag_vent
*		IN 	float	derap
*		IN 	float 	incid
*		IN	float 	rapfreq          frequency ratio (out/in)
*
*		OUT 	float 	derap_valid
*		OUT 	float 	incid_valid
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

int
Valide_vent_givrage (unsigned long Nloop,
		     const int *flag_vent,
		     const float *derap,
		     const float *incid,
		     const double rapfreq,
		     float rempla_derap,
		     float rempla_incid,
		     float *derap_valid, float *incid_valid)
{
  unsigned long i, j;
  int cm, cc, cd, cu;

  if (rapfreq < 1.0)
    return -1;

  if ((long) (rapfreq + 0.5) != rapfreq)
    return -2;

  for (i = 0; i < Nloop; i++)
    {
      /* cm : chiffre des milliers, cc : chiffre des centaines, ... */
      /* divisions entieres */
      cm = flag_vent[i] / 1000;
      cc = (flag_vent[i] - (cm * 1000)) / 100;
      cd = (flag_vent[i] - (cm * 1000) - (cc * 100)) / 10;
      cu = flag_vent[i] % 10;

      /* derapage : flag 1000 */
      if (cm > 0)
	{
	  for (j = i * rapfreq; j < (i + 1) * rapfreq; j++)
	    {
	      derap_valid[j] = rempla_derap;
	    }
	}
      else
	{
	  for (j = i * rapfreq; j < (i + 1) * rapfreq; j++)
	    {
	      derap_valid[j] = derap[j];
	    }
	}


      /* incidence flags 0100 et 0010 */
      if ((cc > 0) || (cd > 0))
	{
	  for (j = i * rapfreq; j < (i + 1) * rapfreq; j++)
	    {
	      incid_valid[j] = rempla_incid;
	    }
	}
      else
	{
	  for (j = i * rapfreq; j < (i + 1) * rapfreq; j++)
	    {
	      incid_valid[j] = incid[j];
	    }
	}
      /* radome givre flag 0002 */
      /*
         if (cu > 1)
         {
         for (j = i * rapfreq; j < (i+1) * rapfreq; j++)
         {
         incid_valid[j] = 0.0;
         derap_valid[j] = 0.0;
         }
         }
         else
         {
         for (j = i * rapfreq; j < (i+1) * rapfreq; j++)
         {
         incid_valid[j] = incid[j];
         derap_valid[j] = derap[j];
         }
         }
       */

    }
  return 0;
}

/* fonction d'enrobage */

int
OP_Valide_vent_givrage (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;
  const float rempla_derap = 0.0;
  const float rempla_incid = 0.0;

  CodRet = Valide_vent_givrage (Nbval,
				(int *) ArgList[0],
				(float *) ArgList[1],
				(float *) ArgList[2],
				*((double *) ArgList[3]),
				rempla_derap,
				rempla_incid,
				(float *) ArgList[4], (float *) ArgList[5]);
  if (CodRet == -1)
    {
      strcpy (DiagExec, "Erreur : rapfreq < 1");
      return OP_FAIL;
    }
  if (CodRet == -2)
    {
      strcpy (DiagExec, "Erreur : rapfreq non-entier");
      return OP_FAIL;
    }
  strcpy (DiagExec, "");
  return OP_OK;
}

void
ID_Valide_vent_givrage (oper * optr)
{
  strcpy (optr->Nom, "Valide_vent_givrage");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Valide_vent_givrage;
  optr->NbArg = 6;

  /* flag_vent */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "unknown";

  /* derap */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "unknown";

  /* incid */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg2.NbVal";	/* identique à derap, pas forcement à flag */
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "unknown";

  /*  double rapfreq */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "unknown";

  /* derap_valid  */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[4].sample = "$Arg2.sample";
  optr->Arg_Car[4].unite = "$Arg2.unit";
  optr->Arg_Car[4].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[4].famille = "$Arg2.famille";
  optr->Arg_Car[4].name = "$Arg2.name + \" selectionne selon \" + $Arg1.name";
  optr->Arg_Car[4].en_name =
    "$Arg2.english_name + \" selected selon \" + $Arg1.english_name";

  /* incid_valid  */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[5].sample = "$Arg3.sample";
  optr->Arg_Car[5].unite = "$Arg3.unit";
  optr->Arg_Car[5].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[5].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[5].famille = "$Arg3.famille";
  optr->Arg_Car[5].name = "$Arg3.name + \" selectionne selon \" + $Arg1.name";
  optr->Arg_Car[5].en_name =
    "$Arg3.english_name + \" selected selon \" + $Arg1.english_name";

}
