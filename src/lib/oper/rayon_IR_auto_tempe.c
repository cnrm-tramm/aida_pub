/*******************************************************************
* OPERATOR      rayon_IR_auto_tempe.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du flux de rayonnement Infra-Rouge avec transformation
* 		automatique de la température en Kelvin si nécessaire.
*		On suppose néanmoins que les températures passées en argument
*		ont la même unité.
*
* DESCRIPTION   On multiplie l'activite brute par un  
*		coefficient de calibration et par la
*		frequence d'acquisition des donnees.
*
* VERSION       1.0
*
*               IN      float   Vth		tension thermopile (Volt)
*               IN      float   Tb		temperature boitier (K ou °C)
*               IN      float   Tc 		temperature coupole (K ou °C)
*		IN 	float	ath		coefficient de sensibilite de la 
*						thermopile
*		IN	float	K 		correction caracteristique de 
*						la liaison thermique boitier coupole
*
*               OUT     float   IR		Flux Infra-rouge (W/m2)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	G. Brogniez LOA Lille  
*
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
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
#include "unit.h"

int
rayon_IR_auto_tempe (unsigned long ndata,
	      float *Vth,
	      float *Tb,
	      float *Tc,
	      float ath,
	      float K,
	      float *IR)
{

  long i;
  float CtoK;
  int flag_info;

/*** constante de Stefan-Boltzman ***/
  float sigma = 5.6698e-8;

  float Tc4, Tb4;
  CtoK = 0.;

  flag_info = auto_tempe_unit (ndata, Tb, &CtoK);

  for (i = 0; i < ndata; i++)
    {
      Tc4 = pow (Tc[i] + CtoK, 4);
      Tb4 = pow (Tb[i] + CtoK, 4);
      IR[i] = ath * (Vth[i]) + sigma * (Tb4 + K * (Tb4 - Tc4));
    }

  return (flag_info);
}

/* fonction d'enrobage */

int
OP_rayon_IR_auto_tempe (unsigned long Nb_Val, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec,
	   "rayon_IR_auto_tempe(%lu ech.), sensibilite=%g, liaison thermique=%g",
	   Nb_Val, *((float *) ArgList[3]), *((float *) ArgList[4]));

  CodRet = rayon_IR_auto_tempe (Nb_Val, (float *) ArgList[0],
			 (float *) ArgList[1], (float *) ArgList[2],
			 *((float *) ArgList[3]),
			 *((float *) ArgList[4]), (float *) ArgList[5]);

  switch (CodRet)
    {
    case 0:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case 1:
      strcat (DiagExec, "; Tempé reconnue en K.");
      break;
    default:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes :par défaut température en K.");
      break;
    }

  return OP_OK;
}

void
ID_rayon_IR_auto_tempe (oper * optr)
{
  strcpy (optr->Nom, "rayon_IR_auto_tempe");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_rayon_IR_auto_tempe;
  optr->NbArg = 6;

  /* Vth */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* Tb */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Kelvin";

  /* Tc */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "Kelvin";

  /* ath */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* K */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  /* IR */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "W/m2";
  optr->Arg_Car[5].famille = " \"rayonnement\" ";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].name = "\"Rayonnement infra-rouge issu de \"+ $Arg1.name";
  optr->Arg_Car[5].en_name =
    "\"Infrared radiation from \"+ $Arg1.english_name";
}
