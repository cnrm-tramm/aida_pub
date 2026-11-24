/****************************************************
*
* OPERATOR     Tair_soni.c   FUNCTION ANSI-C
*
* PURPOSE      Calcul de la temperature de l'air
*	       a partir de la mesure du thermoanemometre
*	       a ultra-sons et du rapport de melange en vapeur d'eau (g/kg).
*
* DESCRIPTION  Application d'une correction
*	       d'humidite Tair = (1 - 0.518.q)Tm 
*
* VERSION      1.4
*
* ARGUMENTS    IN   float  Tsoni    K or C  Temperature mesuree par le TAA
*              IN   float  Rapm     g/kg    rapport de melange en vapeur d'eau 
*          
*              OUT  float  Tair     K or C  temperature statique calculee
*          
* ENTRY        
*          
* SUBPROGRAMS    
*
* FILES     
*
* REFERENCES 
*
* CHANGES 
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT    The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#ifndef K_T0
#define K_T0 (273.15)
#endif
#include "unit_def.h"


int
Tair_soni (const unsigned long NLoop,
	   const float *Tsoni,
	   const float *Rapm,
	   float *Tair)
{
  double q, r, T;
  float CtoK;
  unsigned long i;

  int flag_info_tempe;

 /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Tsoni, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      r = 1.e-3 * Rapm[i];
      q = r / (1. + r);

      T = (1. - 0.518 * q) * (Tsoni[i] + CtoK);

      Tair[i] = T - CtoK;
    }

  return flag_info_tempe;
}

/* la fonction d'enrobage classique */

int
OP_Tair_soni (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Tair_soni, (%lu)", NbVal);

  CodRet = Tair_soni (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2]);

  switch (CodRet)
    {
    case T_EN_K:
      strcat (DiagExec, " Tempe reconnue en Kelvins");
      break;;
    case T_EN_C:
      strcat (DiagExec, " Tempe reconnue en degres Celsius");
      break;;
    case MANQUANTES:
      strcat (DiagExec, "Unite tempe non reconnue");
      return OP_FAIL;
      break;
    }
  return OP_OK;
}

void
ID_Tair_soni (oper * optr)
{
  strcpy (optr->Nom, "Tair_soni");
  optr->Version = "1.0";
  optr->Date = "06/17/97";
  optr->fctptr = OP_Tair_soni;
  optr->NbArg = 3;

  /* Tsoni */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /*  Rapm */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "gram/kg";

  /* Tair */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = " \"temperature\" ";

}
