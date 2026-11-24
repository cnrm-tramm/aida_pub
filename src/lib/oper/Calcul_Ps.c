/*********************************************************
*
* OPERATOR       Calcul_Ps.c  ANSI-C
*
* PURPOSE       Calcul de la pression a partir de 
*		l'altitude, la temperature d'impact, la temperature
*		du point de rosee, de la surpression dynamique, et
*		du QNH.
*		Cet operateur resoud par iterations successives
*		le systeme d'equations. 
*	
*
* DESCRIPTION      
*
* 
* VERSION        $Revision$
*
* ARGUMENTS      IN   float   Alti    
*                IN   float   Tt     
*		 IN   float   Td
*		 IN   float   Dp
*                IN   float   QNH    
*                IN   float   Ra
*		 IN   float   Cpa
*		 IN   float   g 
*
*                OUT  float   Ps
*
* FILES          NONE
*
* REFERENCES       
*              
* COPYRIGHT      Meteo-France
*
* AGREEMENT      Nothing special
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <string.h>
#include <stdio.h>
#include <math.h>
#include "struct_oper.h"

#include "thermo.h"
#include "unit.h"
#include "Tair.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif

int
Calcul_Ps (unsigned long Nbval,
	   const float *Alti,
	   const float *Tt,
	   const float *Td,
	   const float *Dp,
	   const float rf,
	   const float QNH,
	   const float Ra, const float Cpa, const float g, float *Ps)
{
  unsigned long i;

  int niter;

  float CtoK_tt, CtoK_td;
  float Tt_K, Ts_K, Tv_K, Pcal, RapM, ecart_Ps;


  /* Détermination automatique Kelvin/Celsius */
  (void) auto_tempe_unit (Nbval, Tt, &CtoK_tt);
  (void) auto_tempe_unit (Nbval, Td, &CtoK_td);

  for (i = 0; i < Nbval; i++)
    {

      /* initialisation */
      Tt_K = Tt[i] + CtoK_tt;

      Ts_K = Tt_K;
      Tv_K = Tt_K;

      /* formule de Laplace */
      Pcal = QNH * exp (-Alti[i] / (Ra * Tv_K / g));
      Ps[i] = Pcal;
      ecart_Ps = 10.;

      niter = 0;

      while (ecart_Ps > 0.05)
	{

	  /* calcul de la tempe statique */

	  Tt_K = Tt[i] + CtoK_tt;
	  (void) Tair (1, &Tt_K, &(Dp[i]), &Pcal, rf, Ra / Cpa, -1e-10, &Ts_K);

	  /* calcul du rapport de melange */

	  rmel_Td (Td[i] + CtoK_td, Pcal, &RapM);
	  RapM = RapM / 1000.;

	  /* calcul de la temperature virtuelle */

	  tvir (Ts_K, RapM, &Tv_K);

	  /* calcul de la pression par Laplace */

	  Pcal = QNH * exp (-Alti[i] / (Ra * Tv_K / g));

	  ecart_Ps = fabsf (Pcal - Ps[i]);
	  Ps[i] = Pcal;

	  niter = niter + 1;
	}
    }
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Calcul_Ps (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Calcul_Ps(%ld ech.),  %f, %f; ", NbVal,
	   *((float *) ArgList[2]), *((float *) ArgList[3]));

  CodRet = Calcul_Ps (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3],
		      *((float *) ArgList[4]),
		      *((float *) ArgList[5]),
		      *((float *) ArgList[6]),
		      *((float *) ArgList[7]),
		      *((float *) ArgList[8]), (float *) ArgList[9]);

  switch (CodRet)
    {
    case 0:
      return OP_OK;
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Calcul_Ps (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Calcul_Ps");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Calcul_Ps;
  optr->NbArg = 10;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "hPa";

  for (i = 4; i <= 8; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
      optr->Arg_Car[i].unite = "";
    }

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "hPa";
  optr->Arg_Car[9].famille = "\"pression\"";
}
