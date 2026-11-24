/*****************************************************
*
* OPERATOR        DensAirsec.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute the dry air density 
*
* DESCRIPTION 	  Application de l'équation d'état des gaz parfait :
*                        P = rho . Ra . T
*
* VERSION         1.0
*
* ARGUMENTS  IN   float      Ps 	hPa 	Air Pressure	
*            IN   float      Ts 	C or K 	Air temperature	
*
*            OUT  float      Dens	kg/m3	Air density
*                                                
*                                                
* ENTRY           NONE
*               
*
* SUBPROGRAMS     NONE
*
* FILES           NONE
*
* REFERENCES     
*
* CHANGES        
*
*
* COPYRIGHT       Meteo-France/CNRM
*
* AGREEMENT       
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" isfinite() */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* Pour reconnaissance auto d'unité */
#include "unit_def.h"

int
DensAirsec (unsigned long NLoop,
	    const float *Ps,
	    const float *Ts,
	    float Ra,
	    float *Dens)
{
  unsigned long i;
  int flag_info_tempe;
  float CtoK;

  flag_info_tempe = auto_tempe_unit (NLoop, Ts, &CtoK);

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < NLoop; i++)
      {
       Dens[i] = 0./0.; 
      }
    return flag_info_tempe;
   }

  
  for (i = 0; i < NLoop; i++)
    {
      /* test valeur physiquement plausible */
      if (((Ts[i] + CtoK) < 173.) ||
	  ((Ts[i] + CtoK) > 373.) ||
	  (Ps[i] < 1.) ||
	  (Ps[i] > 1500.0))
	{
	  Dens[i] = K_NaN;
	}
      else
	{
	  /* 100.0 pour transformer les hPa en Pa.    */
	  Dens[i] = (100. * Ps[i]) / (Ra * (Ts[i] + CtoK));
	}
    }

  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_DensAirsec (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  const float Ra = 287.05;

  sprintf (DiagExec, "DensAirsec, %lu echant., Ra = %g", NbVal, Ra);

  CodRet = DensAirsec (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       Ra,
		       (float *) ArgList[2]);
  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "OK : T reconnue en Celsius");
      return OP_OK;
    case T_EN_K:
      strcat (DiagExec, "OK: T reconnue en Kelvins");
      return OP_OK;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_OK;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_DensAirsec (oper * optr)
{
  strcpy (optr->Nom, "DensAirsec");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_DensAirsec;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 3;

  /* Ps */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";
  optr->Arg_Car[0].famille = "\"pression\"";

  /* Ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].unite = "K";
  optr->Arg_Car[1].famille = "\"temperature\"";

/* La variable produite            */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[2].sample = "$Arg2.sample";
  optr->Arg_Car[2].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[2].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[2].misval = "$Arg2.misval";
  optr->Arg_Car[2].unite = "kg/m3";
  optr->Arg_Car[2].famille = " \"thermodynamique\" ";
  optr->Arg_Car[2].name = " \"masse volumique de l'air\" ";
  optr->Arg_Car[2].en_name = " \"air volumic mass\" ";

}
