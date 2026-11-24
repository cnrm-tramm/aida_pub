/****************************************************************
* OPERATOR 	Ote_Base  FUNCTION  ANSI-C
* 
* PURPOSE	correction of drifts by mesure of "zero"
*
* DESCRIPTION   Cette fonction enlève un offset à une mesure
*	   	par estimation de la dérive sur des "zéros" périodiques
*
* VERSION       $Revision$
*
* ARGUMENTS	IN   float   X            parametre brut	
*		IN   float   Flag_X       parametre de contrôle indiquant
*		                          les séquences de mesure de zéro
*		IN   float   seuil_bas_Flag_X   Passage à zéro lorsque
*		                                   Flag_X dépasse ce seuil.
*		IN   float   seuil_haut_Flag_X  Fonctionnement normal
*		                                   lorsque flag_X est sous ce seuil.
*		IN   U_int   tps_repons_idx     Temps de réponse (Nombre de points)
*	        IN   int     max_interpol_dist_idx
	        IN   int     max_extrapol_avant_idx  extrapolation autorisée avant
	        IN   int     max_extrapol_apres_idx   extrapolation autorisée après
*		OUT  float   base         l'estimation de la ligne de base.
* 		OUT  float   Xcor 	   parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       2009-02-18 : Prise en compte du cas où l'acquisition s'arrète
*               pendant un passage à zéro. Suppression de l'extrapolation 
*               (en supposant la dérive constante) avant le premier passage à zéro.
*               2008-06-06 : Tous les paramètres du fonctionnement (seuils, 
*               temps de réponse) sont passés en argument. Commentaires
*               d'exécution plus bavards.
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

/* Le #define _HPUX_SOURCE est la pour utiliser la fonction isfinite */
/* #define _HPUX_SOURCE 1 */


#include <math.h>
#include <float.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "struct_oper.h"

/** Remplit base entre i_deb et i_fin-1 avec le mini de X entre i_deb et 
 * i_fin-1, si * (i_fin - i_deb) est plus grand que tps_repons_idx.
 *
 * \param X
 * \param i_deb
 * \param i_fin
 * \param base
 * \param tps_repons_idx
 *
 * \return 1 si un minima a été trouvé
 *         0 sinon.
 */
int
find_and_set_mini (const float *X, unsigned long i_deb, unsigned long i_fin,
		   float *base, unsigned long tps_repons_idx)
{
  unsigned long j;
  unsigned long ignore;
  float min_base;

  if (i_fin <= i_deb)
    {
      return 0;
    }

  if ((i_fin - i_deb) < 1.5 * tps_repons_idx)
    {
      /* Too short ! On ne prend pas en compte */
      (void) fprintf (stderr,
		      "Periode courte ignorée entre indices %lu et %lu !\n",
		      i_deb, i_fin - 1);
      return 0;
    }

  ignore = 0.7 * tps_repons_idx;
  min_base = 1.0e+37;
  for (j = i_deb + ignore; j < i_fin; j++)
    {
      if (X[j] < min_base)
	min_base = X[j];
    }
  if (min_base >= 0.95 * 1.0e+37)	/* prudence test float */
    {
      (void) fprintf (stderr,
		      "min entre %lu et %lu est manquant !\n",
		      i_deb, i_fin - 1);
      return 0;
    }
  else
    {
      (void) fprintf (stderr,
		      "min entre %lu et %lu est : %f\n",
		      i_deb, i_fin - 1, min_base);
      for (j = i_deb; j < i_fin; j++)
	base[j] = min_base;
      return 1;
    }
}

int
Ote_Base (unsigned long NLoop,
	  const float *X,
	  const float *Flag_X,
	  const double seuil_bas_Flag_X,
	  const double seuil_haut_Flag_X,
	  unsigned int tps_repons_idx,
	  int max_interpol_dist_idx,
	  int max_extrapol_avant_idx,
	  int max_extrapol_apres_idx,
	  const float *OK_range, float *base, float *X_cor)
{
  unsigned long i;
  unsigned long borne_fin;
  int Flag_in_serie;
  unsigned long idx_deb_prem_seq, idx_fin_dern_seq;
  register double c1, c2, dt;
  register long d1, d2;
  unsigned long idx_prev_OK, idx_next_OK;
  unsigned long idx_since_last_zero;
  unsigned long dernier_fait;
  float estim;

  /* Toute valeur en-dessous de cst_min_data_valid sera considérée comme manquante.
   * Le résultat sera initialisé par défaut à cst_base_mnq.
   * Il faut que cst_base_mnq < cst_min_data_valid 
   * On a un facteur 10, ça doit suffire */
  const float cst_base_mnq = -1.0e+31;
  const float cst_min_data_valid = -1.0e+30;

  int Nb_seq_zero = 0;

  if (NLoop == 0)
    return 0;

  /* Par défaut, base ne contient que des valeurs manquantes */
  for (i = 0; i < NLoop; i++)
    {
      base[i] = cst_base_mnq;
    }

  /* Recherche des "bons" minima pour construire la série "base" :
   *   On identifie les series ou Flag_X > seuil_haut_Flag_X
   *   Pour chacune de ces périodes, on calcule le mini, et
   * on remplit TOUTE LA PÉRIODE avec ce minimum.
   */
  Flag_in_serie = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (Flag_X[i] > seuil_haut_Flag_X)
	{
	  if (Flag_in_serie == 0)
	    {
	      idx_prev_OK = i;
	      Flag_in_serie = 1;
	    }
	}
      else
	{
	  if (Flag_in_serie == 1)
	    {
	      Flag_in_serie = 0;
	      Nb_seq_zero +=
		find_and_set_mini (X, idx_prev_OK, i, base, tps_repons_idx);
	    }
	}
    }
  /* N'oublions pas le cas où l'acquisition s'arrete pendant 
   * un "passage à zéro" */
  if (Flag_in_serie == 1)
    {
      Nb_seq_zero +=
	find_and_set_mini (X, idx_prev_OK, NLoop, base, tps_repons_idx);
    }

  /* Ce n'est pas la peine d'essayer de faire des interpolations si
   * on n'a pas trouvé de minimum.  */
  if (Nb_seq_zero == 0)
    {
      for (i = 0; i < NLoop; i++)
	{
	  X_cor[i] = K_NaN;
	}
      return Nb_seq_zero;
    }

  /* Recherche du premier non-nul */
  i = 0;
  while ((i < NLoop) && (base[i] < cst_min_data_valid))
    i++;
  if (i < NLoop)
    idx_deb_prem_seq = i;
  else
    {
      /* Normalement (puisque Nb_seq_zero != 0), on n'arrive jamais ici */
      for (i = 0; i < NLoop; i++)
	{
	  X_cor[i] = K_NaN;
	}
      return -2;
    }

  /* Recherche du dernier non-nul */
  if (base[NLoop - 1] < cst_min_data_valid)
    {
      /* Petite particularité : on évite que i=0-1, car i est unsigned !! */
      i = NLoop - 1;
      while ((i > 0) && (base[i] < cst_min_data_valid))
	i--;
      if (i > 0)
	idx_fin_dern_seq = i;
      else
	{
	  /* Normalement (puisque Nb_seq_zero != 0), on n'arrive jamais ici */
	  return -2;
	}
    }

  if (max_extrapol_avant_idx > 0)
    {
      /* Bien qu'on mélange un unsigned (idx_deb_prem_seq) et un signed
       * (max_extrapol_avant_idx), le code suivant est sûr :
       *   1) On sait que max_extrapol_avant_idx > 0
       *   2) Pas de débordement possible : on ne fait le calcul de 
       * (idx_deb_prem_seq - max_extrapol_avant_idx) que si on sait que
       * le résultat n'est pas négatif.
       */
      if (idx_deb_prem_seq < max_extrapol_avant_idx)
	i = 0;
      else
	i = idx_deb_prem_seq - max_extrapol_avant_idx;

      base[i] = base[idx_deb_prem_seq];
      idx_deb_prem_seq = i;
    }

  if (max_extrapol_apres_idx > 0)
    {
      /*  Le code suivant va échouer si
       * (idx_fin_dern_seq + max_extrapol_apres_idx) est trop 
       * grand (overflow). On néglige pour l'instant.
       */
      i = idx_fin_dern_seq + max_extrapol_apres_idx;
      if (i > NLoop - 1)
	i = NLoop - 1;
      base[i] = base[idx_fin_dern_seq];
      idx_fin_dern_seq = i;
    }

  /* Interpolation de "base" */
  borne_fin = idx_fin_dern_seq + 1;
  dernier_fait = idx_deb_prem_seq;
  while (dernier_fait < borne_fin)
    {
      /* recherche de périodes de "manque" */
      i = dernier_fait;
      while ((i < borne_fin) && (base[i] > cst_min_data_valid))
	i++;
      if (i < NLoop)
	{
	  idx_prev_OK = i - 1;
	  /* Maintenant, recherche du suivant OK. */
	  /* On est sur qu'il existe car on a rempli base[borne_fin - 1] */
	  while ((i < borne_fin) && (base[i] < cst_min_data_valid))
	    i++;
	  idx_next_OK = i;
	  /* L'interpolation elle-même */
	  dt = (double) (idx_next_OK - idx_prev_OK);
	  for (i = idx_prev_OK + 1; i < idx_next_OK; i++)
	    {
	      d1 = i - idx_prev_OK;
	      d2 = idx_next_OK - i;
	      if ((d1 < max_interpol_dist_idx)
		  || (d2 < max_interpol_dist_idx))
		{
		  c1 = ((double) d1) / dt;
		  c2 = ((double) d2) / dt;
		  base[i] = c2 * base[idx_prev_OK] + c1 * base[idx_next_OK];
		}
	    }
	  dernier_fait = idx_next_OK;
	}
      else
	dernier_fait = i;
    }

  /* dernière boucle */
  idx_since_last_zero = tps_repons_idx + 1;
  for (i = 0; i < NLoop; i++)
    {
      /* "formattage" de base : misval-> NaN */
      if (base[i] < cst_min_data_valid)
	{
	  base[i] = K_NaN;
	}
      /* Calcul de X_cor */
      if (Flag_X[i] < seuil_bas_Flag_X)
	{
	  idx_since_last_zero++;
	  if (idx_since_last_zero > tps_repons_idx)
	    {
	      estim = X[i] - base[i];
	      if ((estim >= OK_range[0]) && (estim <= OK_range[1]))
		{
		  X_cor[i] = estim;
		}
	      else
		{
		  X_cor[i] = K_NaN;
		}
	    }
	  else
	    X_cor[i] = K_NaN;
	}
      else
	{
	  X_cor[i] = K_NaN;
	  idx_since_last_zero = 0;
	}
    }

  return Nb_seq_zero;
}

/* la fonction d'enrobage classique */

int
OP_Ote_Base (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  /* La distance max à un zéro à laquelle on s'autorise
   * à faire l'interpolation. Pour l'instant, paramétrée "large"
   * en fct du temps de réponse. */
  int max_interpol_dist_idx = *((unsigned int *) ArgList[4]) * 100;
  /* Durée max d'extrapolation, exprimée en nombre de points. */
  /* Version préliminaire : basée sur ArgList[4] (tps_repons_idx). */
  int max_extrapol_avant_idx = 0;
  int max_extrapol_apres_idx = *((unsigned int *) ArgList[4]) * 15;
  float OK_range[] = { 0, FLT_MAX };
  int NCar;

  NCar = sprintf (DiagExec, "Ote_Base : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Ote_Base (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *((float *) ArgList[2]),
		     *((float *) ArgList[3]),
		     *((unsigned int *) ArgList[4]),
		     max_interpol_dist_idx,
		     max_extrapol_avant_idx,
		     max_extrapol_apres_idx,
		     OK_range, (float *) ArgList[5], (float *) ArgList[6]);

  switch (CodRet)
    {
    case -1:
      /* Dans la version actuelle, cela ne devrait jamais arriver */
      strcat (DiagExec, "Alloc. memoire ratée");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "Impossible de déterminer la base");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "%d passage(s) à zéro détecté(s)", CodRet);
      return OP_OK;
    }
}

void
ID_Ote_Base (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Ote_Base");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ote_Base;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 7;
  i = 0;

  /* X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "any";
  i++;

  /* Flag_X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "any";
  i++;

  /* seuil_bas_Flag_X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "any";
  i++;

  /* seuil_haut_Flag_X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "any";
  i++;

  /* tps_repons_idx */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_UI32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "any";
  i++;

  /* base  */
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].misval = "-99999.0";
  optr->Arg_Car[i].unite = "$Arg1.unit";
  optr->Arg_Car[i].famille = "$Arg1.famille";
  i++;

  /* X_cor */
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].misval = "-99999.0";
  optr->Arg_Car[i].unite = "$Arg1.unit";
  optr->Arg_Car[i].famille = "$Arg1.famille";

}
