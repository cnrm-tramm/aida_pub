/****************************************************
*
* OPERATOR     Tair_soni_ha.c   FUNCTION ANSI-C
*
* PURPOSE      Calcul de la temperature de l'air
*	       a partir de la mesure du thermoanemometre
*	       sonique, de l'humidité absolue (g/m3) et 
*	       et de la pression
*
* DESCRIPTION  
*		On part des equations suivantes :
*                  
*		Ta = (1 - 0.518.q).Tsoni
*		q = r/(1+r)
*		r = Ha/Rhoa 
*		Rhoa = Pa/Ra.Ta
*
*		avec 	q = humidite specifique ( g/kg air)
*		     	r = rapport de melange en vapeur d'eau (g/kg air sec)
*			Ha = humidite absolue (g/m3)
*		   	Ta = temperature de l'air
*		     	Pa = pression
*			Ra = Constante specifique l'air sec
*			Tsoni = temperature sonique
*			Rhoa= masse volumique de l'air (kg/m3)
*			
*		L'inconnue est Ta. A partir de ces 
*		formules, on obtient une equation du second
*		degre qui est resolue classiquement.				
*
* VERSION      1.4
*
* ARGUMENTS    IN   float  Tsoni    K or C  Temperature mesuree par le TAA
*              IN   float  Ha       g/m3    rapport de melange en vapeur d'eau 
*              IN   float  Pa       hPa     Pression de l'air 
*          
*              OUT  float  Ta       K or C  temperature statique calculee
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

#define _POSIX_SOURCE
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1
#define _HPUX_SOURCE

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "unit_def.h"
#ifndef K_T0
#define K_T0 (273.15)
#endif
#ifndef K_Ra
#define K_Ra (8.314510 / 0.028964)
#endif
#define T_EN_C 0
#define T_EN_K 1
#define MANQUANTES 3

int *
Tair_soni_ha (const unsigned long NLoop,
	      const float *Tsoni, const float *Ha, const float *Pa, float *Ta)
{
  double Ts, Ra, T;
  float CtoK;
  double x, b, c, delta;
  static int tab_CR[6];
  int flag_info;
  double alpha = 0.518;
  int nb_T_mnq, nb_P_mnq, nb_Ha_mnq;
  int nb_entree_hors_gamme;
  int nb_discrim_neg;

  unsigned long i;

  /* Détermination automatique Kelvin/Celsius */
  flag_info = auto_tempe_unit (NLoop, Tsoni, &CtoK);

  if (flag_info == MANQUANTES)
    {
      /* la totalité du vecteur est en données manquantes */
      /* on produit quand un vecteur de sortie avec que des
         valeurs manquantes */
      for (i = 0; i < NLoop; i++)
	{
	  Ta[i] = 0. / 0.;	/* NaN */
	}
      tab_CR[0] = flag_info;
      tab_CR[1] = NLoop;
      tab_CR[2] = 0;
      tab_CR[3] = 0;
      tab_CR[4] = 0;
      tab_CR[5] = 0;
      return tab_CR;
    }

  Ra = K_Ra;			/* Constante specifique de l'air sec */

  nb_T_mnq = nb_P_mnq = nb_Ha_mnq = 0;
  nb_entree_hors_gamme = 0;
  nb_discrim_neg = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (Tsoni[i]))
	{
	  Ta[i] = 0.0 / 0.0;
	  nb_T_mnq++;
	  continue;
	}
      if (!isfinite (Pa[i]))
	{
	  Ta[i] = 0.0 / 0.0;
	  nb_P_mnq++;
	  continue;
	}
      if (!isfinite (Ha[i]))
	{
	  Ta[i] = 0.0 / 0.0;
	  nb_Ha_mnq++;
	  continue;
	}

      Ts = Tsoni[i] + CtoK;
      if ((Ts < 170.))
	{
	  Ta[i] = 0.0 / 0.0;
	  nb_entree_hors_gamme++;
	  continue;
	}

      if ((Pa[i] < 0.1) || (Ha[i] < -10.))
	{
	  Ta[i] = 0.0 / 0.0;
	  nb_entree_hors_gamme++;
	  continue;
	}

      /* Calcul des coefficients de l'equations du second degre */


      /* a = 1 */
      x = (100. * Pa[i]) / (Ha[i] * 1.e-3 * Ra);
      b = x - ((1. - alpha) * Ts);
      c = -x * Ts;


      /* calcul du discriminant */
      delta = b * b - 4. * c;

      if (delta < 0.)
	{
	  fprintf (stderr, "[%lu]: Discriminant negatif !!\n", i);
	  Ta[i] = 0.0 / 0.0;
	  nb_discrim_neg++;
	  continue;
	}

      /* c < 0 donc delta >0 toujours 2 solutions */
      /* le produit c/a des racines est negatif, une seule
         racine est positive */

      T = (sqrt (delta) - b) / 2.;

      Ta[i] = T - CtoK;
    }

  tab_CR[0] = flag_info;
  tab_CR[1] = nb_T_mnq;
  tab_CR[2] = nb_P_mnq;
  tab_CR[3] = nb_Ha_mnq;
  tab_CR[4] = nb_entree_hors_gamme;
  tab_CR[5] = nb_discrim_neg;
  return tab_CR;
}

/* la fonction d'enrobage classique */

int
OP_Tair_soni_ha (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int *CodRet;

  sprintf (DiagExec, "Tair_soni_ha, (%lu ech.)", NbVal);

  CodRet = Tair_soni_ha (NbVal,
			 (float *) ArgList[0],
			 (float *) ArgList[1],
			 (float *) ArgList[2], (float *) ArgList[3]);
  switch (CodRet[0])
    {
    case T_EN_C:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case T_EN_K:
      strcat (DiagExec, "; Tempé reconnue en K.");
      break;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Toutes valeurs manquantes : unité de température non reconnue.");
      break;
    }
  sprintf (DiagExec + strlen (DiagExec), "; %d T mnq", CodRet[1]);
  sprintf (DiagExec + strlen (DiagExec), "; %d P mnq", CodRet[2]);
  sprintf (DiagExec + strlen (DiagExec), "; %d Ha mnq", CodRet[3]);
  sprintf (DiagExec + strlen (DiagExec), "; %d entrees hors gamme",
	   CodRet[4]);
  sprintf (DiagExec + strlen (DiagExec), "; %d racines incalc.", CodRet[5]);

  return OP_OK;
}

void
ID_Tair_soni_ha (oper * optr)
{
  strcpy (optr->Nom, "Tair_soni_ha");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Tair_soni_ha;
  optr->NbArg = 4;

  /* Tsoni */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* Ha */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "gram/m3";

  /* Pa */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  /* Ta */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  /*optr->Arg_Car[3].misval = "-9999."; */
  optr->Arg_Car[3].misval = "$Arg2.misval";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = " \"temperature\" ";
  optr->Arg_Car[3].name = " \"temperature de l'air\" ";
}
