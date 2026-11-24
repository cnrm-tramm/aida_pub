/*****************************************************
*
* OPERATOR        V_Air_Ts.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute air speed from dynamical pressure.
*
* DESCRIPTION     Uses one of the forms of the St-Venant's formula
*                 to compute air speed out of static pressure,
*                 total pressure, and static temperature.
*
* VERSION         $Revision$
*
* ARGUMENTS  IN   float      Ts  K or C      Tempe. ambiante (statique)
*            IN   float      Ps  any         Pression statique
*            IN   float      dP  same as Ps  dynamical pressure
*            IN   float      cp              Chaleur massique a P. constante
*            IN   float  rsurcp              r/cp  (et r = cp-cv, classique...)
*
*            OUT  float      Vp  m/s         Air Speed
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
*
* CHANGES        1.3  adapted to changes in categorie's definition
*                1.2  switched args order/added args' sampling description
*
*
* COPYRIGHT       Meteo-France/CNRM
*
* AGREEMENT       
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#ifndef K_T0
#define K_T0 (273.15)
#endif


unsigned long
V_Air_Ts (unsigned long NLoop,
	  const float *Ts,
	  const float *Ps,
	  const float *dP,
	  const float cp,
	  const float rsurcp,
	  float *Vp)
{
  unsigned long i, nb_neg;
  register float T, Vp2;

  nb_neg = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (*Ts < 100.0)
	T = *Ts + K_T0;
      else
	T = *Ts;

      if (*dP < 0.0)
	{
	  *Vp = 0.0;
	  nb_neg++;
	}
      else
	{
	  Vp2 = 2.0 * cp * T * (pow ((*Ps + *dP) / *Ps, rsurcp) - 1.0);
	  *Vp = sqrt (Vp2);
	}

      Ts++;
      Ps++;
      dP++;
      Vp++;
    }
  return nb_neg;
}


/* la fonction d'enrobage classique */

int
OP_V_Air_Ts (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "V_Air_Ts, %lu echant.", NbVal);

  CodRet = V_Air_Ts (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]), (float *) ArgList[5]);
  if (CodRet != 0)
    {
      (void) sprintf (DiagExec + strlen (DiagExec), " %lu dP<0", CodRet);
    }
  return OP_OK;
}

void
ID_V_Air_Ts (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "V_Air_Ts");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_V_Air_Ts;
  optr->NbArg = 6;

  /* Ts */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  /* Ps */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx++;

  /* dP */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "$Arg2.unit";
  idx++;

/* La première constante thermodynamique : cp */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "J K-1 kg-1";
  idx++;

  /* rsurcp */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "";
  idx++;

  /* La variable produite : Vp           */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[idx].sample = "$Arg3.sample";
  optr->Arg_Car[idx].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg3.ref_time";
  /* l'unite est toujours la meme */
  optr->Arg_Car[idx].unite = "m/s";
  optr->Arg_Car[idx].famille = " \"vitesse\" ";
  optr->Arg_Car[idx].name = " \"vitesse de l'air\" ";
  optr->Arg_Car[idx].en_name = " \"True air speed\" ";
  idx++;
}
