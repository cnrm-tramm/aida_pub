/*****************************************************
*
* OPERATOR         Ote_Base_auto.c   FUNCTION  ANSI-C
*
* PURPOSE          suppress an offset
*
* DESCRIPTION      
*
* VERSION          $Revision$
*
* ARGUMENTS  IN    float  X        any           Input Var.
*            IN    float  Flag_X   bit           Flag True_measure/zero
*            OUT   float  X_cor    same as X     Calculated base offset.
*            OUT   float  X_cor    same as X     "corrected" var
*
*                                                
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          1.1  original version
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE est la pour utiliser la fonction isfinite */
#define _HPUX_SOURCE 1

#include <math.h>
#include <float.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "struct_oper.h"

#include "Ote_Base.h"

/** Essaye de calculer les 2 seuils de séparation d'une distribution
 * bimodale.
 *
 * Utilise la moyenne d'ensemble comme seuil entre les 2 modes.
 *
 * \param NLoop
 * \param Flag_X
 * \param seuil_bas_Flag_X
 * \param seuil_haut_Flag_X
 */
void
Calcul_seuil_bimod (size_t NLoop, const float *Flag_X,
		    double *seuil_bas_Flag_X, double *seuil_haut_Flag_X)
{
  size_t i, idx_inf, idx_sup;
  double moy, moy_inf, moy_sup;
  double ect_inf = 0.0;
  double ect_sup = 0.0;
  double milieu;

  /* Détermination de la moyenne */
  moy = 0;
  for (i = 0; i < NLoop; i++)
    {
      moy += (double) Flag_X[i];
    }
  moy /= (double) NLoop;

  /* Détermination de la moyenne des >moyenne, et des <moyenne */
  moy_inf = 0;
  moy_sup = 0;
  idx_inf = 0;
  idx_sup = 0;
  for (i = 0; i < NLoop; i++)
    {
      if ((double) Flag_X[i] < moy)
	{
	  moy_inf += (double) Flag_X[i];
	  idx_inf++;
	}
      else
	{
	  moy_sup += (double) Flag_X[i];
	  idx_sup++;
	}
    }
  moy_inf /= (double) idx_inf;
  moy_sup /= (double) idx_sup;

  /* Détermination de l'écart-type des >moyenne, et des <moyenne */
  for (i = 0; i < NLoop; i++)
    {
      if ((double) Flag_X[i] < moy)
	{
	  ect_inf += pow (((double) Flag_X[i] - moy_inf), 2.0);
	}
      else
	{
	  ect_sup += pow (((double) Flag_X[i] - moy_sup), 2.0);
	}
    }
  ect_inf = sqrt (ect_inf / (double) idx_inf);
  ect_sup = sqrt (ect_sup / (double) idx_sup);

  /* C'est fini */
  milieu = (moy_inf + moy_sup) / 2.0;
  *seuil_bas_Flag_X = moy_inf + 5 * ect_inf;
  if (*seuil_bas_Flag_X > milieu)
    *seuil_bas_Flag_X = milieu;
  *seuil_haut_Flag_X = moy_sup - 5 * ect_sup;
  if (*seuil_haut_Flag_X < milieu)
    *seuil_haut_Flag_X = milieu;
}

int
Ote_Base_auto (unsigned long NLoop, const float *X,
	       const float *Flag_X, double *seuil_bas_Flag_X,
	       double *seuil_haut_Flag_X, int *delai_echant,
	       int *max_interpol_dist_idx,
	       int *max_extrapol_avant_idx,
	       int *max_extrapol_apres_idx, const float *OK_range,
	       float *base, float *X_cor)
{
  int CR;

  Calcul_seuil_bimod (NLoop, Flag_X, seuil_bas_Flag_X, seuil_haut_Flag_X);
  /* TODO : déterminer delai à partir de la forme de l'exponentielle
   * post-passage zéro. */
  *delai_echant = 30;
  *max_extrapol_avant_idx = 0;
  *max_extrapol_apres_idx = *delai_echant * 15;
  *max_interpol_dist_idx = 1000;

  CR = Ote_Base (NLoop, X, Flag_X,
		 *seuil_bas_Flag_X,
		 *seuil_haut_Flag_X, *delai_echant,
		 *max_interpol_dist_idx,
		 *max_extrapol_avant_idx,
		 *max_extrapol_apres_idx, OK_range, base, X_cor);
  return CR;
}

/* la fonction d'enrobage classique */

int
OP_Ote_Base_auto (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  /*  Les "constantes" suivantes pourraient être passées en argument,
     pour faire un opérateur vraiment universel.  */
  double seuil_bas_Flag_X = -5e+33;
  double seuil_haut_Flag_X = -5e+33;
  int max_interpol_dist_idx;
  int max_extrapol_avant_idx;
  int max_extrapol_apres_idx;
  int delai;
  float OK_range[] = { 0, FLT_MAX };
  int NCar;

  NCar = sprintf (DiagExec, "Ote_Base_auto : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Ote_Base_auto (NbVal,
			  (float *) ArgList[0],
			  (float *) ArgList[1],
			  &seuil_bas_Flag_X,
			  &seuil_haut_Flag_X,
			  &delai,
			  &max_interpol_dist_idx,
			  &max_extrapol_avant_idx,
			  &max_extrapol_apres_idx,
			  OK_range, (float *) ArgList[2],
			  (float *) ArgList[3]);

  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "Alloc. memoire ratée");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "Impossible de déterminer la base");
      return OP_FAIL;
    default:
      sprintf (DiagExec,
	       "OK: Seuils calculés : inf= %f, sup= %f, delai = %d",
	       seuil_bas_Flag_X, seuil_haut_Flag_X, delai);

      return OP_OK;
    }
}

void
ID_Ote_Base_auto (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Ote_Base_auto");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ote_Base_auto;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 4;

  /* X */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Flag_X */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* base */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "-99999.0";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  optr->Arg_Car[idx].famille = "$Arg1.famille";
  idx++;

  /* X_cor */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "-99999.0";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  optr->Arg_Car[idx].famille = "$Arg1.famille";
  idx++;

}
