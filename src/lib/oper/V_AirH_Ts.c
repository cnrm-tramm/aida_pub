/*****************************************************
*
* OPERATOR        V_AirH_Ts.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute the speed of air relative to platform
*
* DESCRIPTION     Uses one of the forms of the St-Venant's formula
*                 to compute air speed out of static pressure,
*                 dynamic pressure, static temperature, and 
*		  water vapor mixing ratio.
*
* VERSION         1.4
*
* ARGUMENTS  IN   float   Ts     K or C      Ambiant ("Static") Temperature
*            IN   float   Ps     any         Ambiant ("Static") Pressure
*            IN   float   dP     same as Ps  Dynamical Pressure
*	     IN   float   rapmel g/kg        water vapor mixing ratio
*            IN   float   cp                 Chaleur massique a P. constante for dry air
*            IN   float   rsurcp             r_a/cp_a pour l'air sec (et r = cp-cv, classique...)
*
*            OUT  float   Vp     m/s         Air Speed
*                                                
*                                                
* ENTRY           NONE
*               
*
* SUBPROGRAMS     NONE
*
* FILES           NONE
*
* REFERENCES      "Mecanique des fluides", by S. Candel, Dunod.
*
*                 Bulletin NCAR/RAF Nr 23, Feb 87, by D. Lenschow and
*                   P. Spyers-Duran
*
*		  "Meteorologie Generale", 1977 edition, J.P. Triplet & G. Roche, 
*		  cole Nationale de la Meteorologie, p 56.
*
*
* CHANGES        1.3  adapted to changes in categorie's definition
*
*
* COPYRIGHT       Meteo-France/CNRM
*
* AGREEMENT       
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "unit_def.h" 

#ifndef K_T0
#define K_T0 (273.15)
#endif


int
V_AirH_Ts (unsigned long NLoop,
	   const float *Ts,
	   const float *Ps,
	   const float *dP,
	   const float *rapmel, 
	   const float cp, 
	   const float rsurcp, 
	   float *Vp)
{
  unsigned long i;
  float T, Vp2;
  float cph, rh_sur_cph, CtoK, r_kgkg;
  int flag_info;

  /* Détermination automatique Kelvin/Celsius */
  flag_info = auto_tempe_unit (NLoop, Ts, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      T = Ts[i] + CtoK;
      r_kgkg = rapmel[i] / 1000.;

      cph = cp * (1. + 1.85 * r_kgkg) / (1. + r_kgkg);
      rh_sur_cph = rsurcp * (1. + 1.608 * r_kgkg) / (1 + 1.85 * r_kgkg);

      if (dP[i] <= 0.0)
	Vp[i] = 0.0;
      else
	{
	  Vp2 =
	    2.0 * cph * T * (pow ((Ps[i] + dP[i]) / Ps[i], rh_sur_cph) - 1.0);
	  Vp[i] = sqrt (Vp2);
	}
    }
  return flag_info;
}


/* la fonction d'enrobage classique */
#include "struct_oper.h"

int
OP_V_AirH_Ts (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_V_AirH_Ts, NbVal=%ld, Args=();", NbVal);

  CodRet = V_AirH_Ts (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3],
		      *((float *) ArgList[4]),
		      *((float *) ArgList[5]), (float *) ArgList[6]);

   switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case T_EN_K:
      strcat (DiagExec, "; Tempé reconnue en K.");
      break;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; BUG!! Code retour inattendu.");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_V_AirH_Ts (oper * optr)
{
  strcpy (optr->Nom, "V_AirH_Ts");
  optr->Version = "1.4";
  optr->Date = "08/26/96";
  optr->fctptr = OP_V_AirH_Ts;
  optr->NbArg = 7;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "hPa";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "gram/kg";

/* Les Constantes thermodynamiques */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";

/* La variable produite            */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[6].sample = "$Arg3.sample";
  optr->Arg_Car[6].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[6].ref_time = "$Arg3.ref_time";
  /* l'unite est toujours la meme */
  optr->Arg_Car[6].unite = "m/s";

}
