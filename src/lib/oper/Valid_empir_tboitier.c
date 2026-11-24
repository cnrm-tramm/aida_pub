/****************************************************************
* OPERATOR 	Valid_empir_tboitier  FUNCTION  ANSI-C
*
* PURPOSE	Validation empirique des valeurs de T_boîtier des
*               radiomètres IR.
*
* DESCRIPTION   Cette fonction detecte les valeurs hors de la zone
*               déterminee empiriquement (P. Bergue + B. Piguet)
*		a partir des mesures de la Campagnes CAPITOUL.
*               Cet operateur cree un nouveau vecteur "valid_T" qui permet
*               d'indiquer si une mesure d'IR est "valide".
*
*
* VERSION         1.1
*
* ARGUMENTS 	IN 	float 	RGD    Rayonnement global descendant (W/m2).
*           	IN 	float 	Tb     Température de boîtier.
*           	IN 	float 	Tair   Température de l'air.
*           	IN 	float 	Typ_instru   indice donnnant l'appareil (et donc les lois empiriques)
*
* 		OUT 	float 	flag_T indicateur de validation du T_boîtier
*                           --> 0 si OK
*                           --> +1 si T_boîtier - Tair trop fort
*                           --> -1 si T_boîtier - Tair trop faible
*                           --> -10 si RGD trop faible (<-1 W/m2)
*                           --> +10 si RGD trop fort (>1600 W/m2)
*                           --> -9999 si RGD ou Tair manquant (ou inclusif)
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCES	NONE
*
* CHANGES       1.2
*
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

/* Pour la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Valid_empir_tboitier (unsigned long Nloop,
		      const float *RGD,
		      const float *Tb,
		      const float *Tair,
		      const int Typ_instru,
		      float *flag_T, unsigned long *Tab_diagno)
{
  unsigned long i;
  unsigned long nb_sup, nb_inf, nb_RG_sup, nb_RG_inf, nb_NaN, nbOK;
  float Seuil_max, coef_max_1[2], coef_max_2[2];
  float Seuil_min, coef_min_1[2], coef_min_2[2];

  float Delta_T, Limite_Delta_T;

  /* TODO : valider vraiment les coefficients */
  switch (Typ_instru)
    {
    case 1:			/* Schenk échantillonné à 60 s */
      /* Seuil changement loi max */
      Seuil_max = 480;
      /* Seuil changement loi min */
      Seuil_min = 250;
      coef_max_1[0] = 4.0;
      coef_max_1[1] = 0.0145833;
      coef_max_2[0] = 11.0;
      coef_max_2[1] = 0.0;
      coef_min_1[0] = -4.5;
      coef_min_1[1] = 0.010;
      coef_min_2[0] = -2.8;
      coef_min_2[1] = 0.00320;
      break;
    case 2:			/* Schenk échantillonné à 1800 s */
      Seuil_max = 730;
      Seuil_min = 400;
      coef_max_1[0] = 4.0;
      coef_max_1[1] = 0.00684932;
      coef_max_2[0] = 9.0;
      coef_max_2[1] = 0.0;
      coef_min_1[0] = -3.5;
      coef_min_1[1] = 0.00625;
      coef_min_2[0] = -1.72727;
      coef_min_2[1] = 0.00181818;
      break;
    case 3:			/* CNR1 pas ventilé échantillonné à 10 ou 60 s */
      Seuil_max = 300;
      Seuil_min = 150;
      coef_max_1[0] = 4.0;
      coef_max_1[1] = 0.0133333;
      coef_max_2[0] = 8.0;
      coef_max_2[1] = 0.0;
      coef_min_1[0] = -6.50 ;
      coef_min_1[1] = 0.0233333;
      coef_min_2[0] = -3.22222 ;
      coef_min_2[1] = 0.00148148;
      break;
    case 4:			/* CNR1  ventilé échantillonné à 60 s */
      Seuil_max = 200;
      Seuil_min = 200;
      coef_max_1[0] = 2.0;
      coef_max_1[1] = 0.0040;
      coef_max_2[0] = 2.61538;
      coef_max_2[1] = 0.000923077;
      coef_min_1[0] = -2.50;
      coef_min_1[1] = 0.0;
      coef_min_2[0] = -2.65385;
      coef_min_2[1] = 0.000769231;
      break;
    }

  nb_sup = 0;
  nb_inf = 0;
  nb_RG_sup = 0;
  nb_RG_inf = 0;
  nb_NaN = 0;
  nbOK = 0;

  /* Boucle de traitement */

  for (i = 0; i < Nloop; i++)
    {
      flag_T[i] = 0.;
      Delta_T = 0.;
      /* Valeurs Tb manquantes ? */
      if ((isfinite (Tair[i])) && (isfinite (Tb[i])))
	{
	  Delta_T = Tb[i] - Tair[i];
	}
      else
	{
	  (void) printf ("%lu, Tb : %f, Tair : %f \n", i, Tb[i], Tair[i]);
	  nb_NaN = nb_NaN + 1;
	  flag_T[i] = -9999.;
	  continue;
	}

      /* Valeurs RGD/Tair manquantes ?  */
      if (!isfinite (RGD[i]))
	{
	  nb_NaN = nb_NaN + 1;
	  flag_T[i] = -9999.;
	}
      else
	{
	  if (RGD[i] < -1)
	    /* RGD trop faible) */
	    {
	      flag_T[i] = -10.;
	      nb_RG_inf = nb_RG_inf + 1;
	      continue;
	    }
	  if (RGD[i] > 1600.)
	    /* RGD trop fort) */
	    {
	      flag_T[i] = +10.;
	      nb_RG_sup = nb_RG_sup + 1;
	      continue;
	    }

	  if (RGD[i] < Seuil_max)
	    {
	      Limite_Delta_T = coef_max_1[1] * RGD[i] + coef_max_1[0];
	    }
	  else
	    {
	      Limite_Delta_T = coef_max_2[1] * RGD[i] + coef_max_2[0];
	    }
	  if (Delta_T > Limite_Delta_T)
	    {
	      flag_T[i] = +1.;
	      nb_sup = nb_sup + 1;
	      (void)
		printf
		("%lu, RGD : %f, Delta_T : %f,  Limite_Delta_T_max : %f,  Seuil_max : %f\n",
		 i, RGD[i], Delta_T, Limite_Delta_T, Seuil_max);
	      continue;
	    }

	  if (RGD[i] < Seuil_min)
	    {
	      Limite_Delta_T = coef_min_1[1] * RGD[i] + coef_min_1[0];
	    }
	  else
	    {
	      Limite_Delta_T = coef_min_2[1] * RGD[i] + coef_min_2[0];
	    }
	  if (Delta_T < Limite_Delta_T)
	    {
	      flag_T[i] = -1.;
	      nb_sup = nb_sup + 1;
	      (void)
		printf
		("%lu, RGD : %f, Delta_T : %f,  Limite_Delta_T_min : %f,  Seuil_min : %f\n",
		 i, RGD[i], Delta_T, Limite_Delta_T, Seuil_min);
	      continue;
	    }

	  /* Tout est coherent ...au niveau mesure mais on peut avoir
	   */
	  nbOK = nbOK + 1;
	  flag_T[i] = 0.;
	}
    }
  /* La boucle est finie... */

  /* Test de validité interne */
  if (nb_sup + nb_inf + nb_RG_sup + nb_RG_inf + nb_NaN + nbOK != Nloop)
    {
      (void) fprintf (stderr, "internal error : \n");
    }
  /*  */

  Tab_diagno[0] = nbOK;
  Tab_diagno[1] = nb_sup;
  Tab_diagno[2] = nb_inf;
  Tab_diagno[3] = nb_RG_sup;
  Tab_diagno[4] = nb_RG_inf;
  Tab_diagno[5] = nb_NaN;
  return nb_sup + nb_inf;
}

/* fonction d'enrobage */

int
OP_Valid_empir_tboitier (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  unsigned long toto[6];

  /* sprintf (DiagExec,""); */

  CodRet = Valid_empir_tboitier (Nbval,
				 (float *) ArgList[0],
				 (float *) ArgList[1],
				 (float *) ArgList[2],
				 *((int *) ArgList[3]),
				 (float *) ArgList[4], toto);

  sprintf (DiagExec,
	   "%lu valeurs (sur %lu) rejetée(s) [s:%lu, i:%lu, Rs:%lu, Ri:%lu, n:%lu]",
	   CodRet, Nbval, toto[1], toto[2], toto[3], toto[4], toto[5]);
  return OP_OK;
}

void
ID_Valid_empir_tboitier (oper * optr)
{
  int idx=0;

  strcpy (optr->Nom, "Valid_empir_tboitier");
  optr->Version = "1.0";
  optr->Date = "13/09/07";
  optr->fctptr = OP_Valid_empir_tboitier;
  optr->NbArg = 5;
  optr->misval_auto = 1;	/* Fvb remplacera les misval par NaN */

  /* RGD */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].unite = "";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  idx++;

  /* Tb */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].unite = "";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  idx++;

  /* Tair */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].unite = "";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  idx++;

  /* Typ_instru */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_I32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].unite = "";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  idx++;

  /* Flag */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "";
  optr->Arg_Car[idx].misval = NULL;
  optr->Arg_Car[idx].name = " \"Flag de validité de T_boitier\" ";
  optr->Arg_Car[idx].famille = " \"controle\" ";
  idx++;
}
