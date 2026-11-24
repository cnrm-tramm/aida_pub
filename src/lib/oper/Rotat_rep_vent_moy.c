/*****************************************************
*
* OPERATOR         Rotat_rep_vent_moy.c   FUNCTION  ANSI-C
*
* PURPOSE          rotates wind coordinates to a mean-wind born coordinate system.
*
* DESCRIPTION      Converts coordinates of a 3D-vector expressed in
*                  a Earth-related cartesians system to a mean-vector
*                  born referential, so that :
*                               mean(v) = 0
*                               mean(w) = 0
*                               mean(v'w') = 0
*                     
*
* VERSION          $Revision$
*
* ARGUMENTS  IN    float   u   any         East component, from West
*            IN    float   v   same as u   North component, from South
*	     IN	   float   w   same as u   Vertical component, from ground
*	     IN	   int     flag_r          1 pour faire les 3 rotations, 0 pour les 2 premières.
*            OUT   float   u_r same as u   Component along mean vector
*                                            (Positif forward)
*            OUT   float   v_r same as u   Component transverse to mean
*                                            vector axe (mean(v) = 0)
*            OUT   float   w_r same as u   Component transverse to mean
*                                             vector axe (>0 up)
*
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       Bessemoulin, P. 1993 : Méthodes expérimentales de 
*                  détermination des flux de surface, Note de centre 
*                  CNRM/GMEI Nr 6.
*
*
* CHANGES          1.1  Initial version
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED
#define _HPUX_SOURCE

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include <float.h>
#include "struct_oper.h"

#define ROT_OK	 0
#define ROT_NOVAL	1

int
Rotat_rep_vent_moy (const unsigned long NLoop,
		    const float *u,
		    const float *v,
		    const float *w,
		    int flag_r,
		    float *u_r, float *v_r, float *w_r, double info_tab[11])
{
  unsigned long i, j, n_iter;
  /* Composantes moyennes du vent... */
  double V_h_m, V_m;
  /* ep = epsilon = angle de rotation dans le plan horizontal */
  double co_ep, si_ep;
  /* th = theta = angle de rotation dans le plan vertical contenant le vent moyen */
  double co_th, si_th;
  /* be = beta = autour de l'axe du vent moyen pour minimiser moy(w'v') */
  double co_be, si_be;
  double var_v, var_w, covar_vw;
  /* Pour l'iteration */
  double sol1, sol2, new_co_be, K;

  /* Phase 1.1 : calcul des composantes moyennes
   * On crée un bloc avec des variables locales
   * pour faciliter l'optimisation. */
  {
    register double u_m, v_m, w_m;

    u_m = 0.0;
    v_m = 0.0;
    w_m = 0.0;
    j = 0;
    for (i = 0; i < NLoop; i++)
      {
	if (isfinite (u[i]) && isfinite (v[i]) && isfinite (w[i]))
	  {
	    u_m += u[i];
	    v_m += v[i];
	    w_m += w[i];
	    j++;
	  }
      }
    if (j <= 0)
      {
	/* on met les vecteurs de sortie a NaN (modif du 09/06/2000) */
	for (i = 0; i < NLoop; i++)
	  {
	    u_r[i] = 0. / 0.;
	    v_r[i] = 0. / 0.;
	    w_r[i] = 0. / 0.;
	  }
	return ROT_NOVAL;
      }
    /* Si tout va bien, on continue */
    u_m /= j;
    v_m /= j;
    w_m /= j;
    info_tab[0] = j;

    /* vent_horizontal_moyen */
    V_h_m = sqrt (u_m * u_m + v_m * v_m);
    /* vent_moyen  */
    V_m = sqrt (V_h_m * V_h_m + w_m * w_m);
    info_tab[1] = V_m;

    /* Phase 1.2 : calcul des angles de rotation */

    /* Si vent moyen nul, ou trop faible pour la précision des calculs,
     * pas de rotation */
    if (fabs (V_h_m) < FLT_MIN * j)
      {
	co_ep = 1.0;
	si_ep = 0.0;
      }
    else
      {
	co_ep = u_m / V_h_m;
	si_ep = v_m / V_h_m;
      }

    /* Si vent moyen trop faible pour les calculs,  theta = 0 */
    if (fabs (V_m) < FLT_MIN * j)
      {
	co_th = 1.0;
	si_th = 0.0;
      }
    else if (fabs (w_m / V_m) > 0.342)
      {				/* Si pente(écoulement) > 20 deg, SUSPECT ! */
	co_th = 0.939692621;	/* cos (20 deg) */
	/* sinus correspondant, en gardant le signe)   */
	si_th = copysign (sqrt (1 - (co_th * co_th)), w_m / V_m);
      }
    else
      {
	co_th = V_h_m / V_m;
	si_th = w_m / V_m;
      }
  }

  /* Phase 1.3 : Application de la matrice de rotation partielle */
  {
    register double M11, M12, M13, M21, M22, M23, M31, M32, M33;
    M11 = co_ep * co_th;
    M12 = si_ep * co_th;
    M13 = si_th;
    M21 = -si_ep;
    M22 = co_ep;
    M23 = 0.0;
    M31 = -co_ep * si_th;
    M32 = -si_ep * si_th;
    M33 = co_th;
    for (i = 0; i < NLoop; i++)
      {
	u_r[i] = M11 * u[i] + M12 * v[i] + M13 * w[i];
	v_r[i] = M21 * u[i] + M22 * v[i] + M23 * w[i];
	w_r[i] = M31 * u[i] + M32 * v[i] + M33 * w[i];
      }
  }
  /* Arrivés ici, u_r est définitivement calculé. 
   * Calcul des statistique :
   *    moyennes de tous  (u_r, v_r, w_r)
   *    Var et covar v, w
   */
  {
    register double u_m, v_m, w_m;
    register double x_tmp, y_tmp;

    u_m = 0.0;
    v_m = 0.0;
    w_m = 0.0;
    j = 0;
    for (i = 0; i < NLoop; i++)
      {
	if (isfinite (u_r[i]) && isfinite (v_r[i]) && isfinite (w_r[i]))
	  {
	    u_m += u_r[i];
	    v_m += v_r[i];
	    w_m += w_r[i];
	    j++;
	  }
      }
    if (j <= 0)
      {
	return ROT_NOVAL;
      }
    /* Si tout va bien, on continue */
    u_m /= j;
    v_m /= j;
    w_m /= j;
    info_tab[2] = u_m;
    info_tab[3] = v_m;
    info_tab[4] = w_m;

    if (flag_r == 0)
      {
	for (j = 5; j < 11; j++)
	  info_tab[j] = 0;
	return ROT_OK;
      }
    var_v = 0.0;
    var_w = 0.0;
    covar_vw = 0.0;
    j = 0;
    for (i = 0; i < NLoop; i++)
      {
	if (isfinite (u_r[i]) && isfinite (v_r[i]) && isfinite (w_r[i]))
	  {
	    x_tmp = v_r[i] - v_m;
	    y_tmp = w_r[i] - w_m;
	    var_v += x_tmp * x_tmp;
	    var_w += y_tmp * y_tmp;
	    covar_vw += x_tmp * y_tmp;
	    j++;
	  }
      }
    if (j <= 0)
      {
	return ROT_NOVAL;
      }
    var_v /= j;
    var_w /= j;
    covar_vw /= j;
    info_tab[5] = var_v;
    info_tab[6] = var_w;
    info_tab[7] = covar_vw;
  }
  K = covar_vw / (var_v + var_w);

  /* Phase 1.4 : Iterations pour calcul du dernier angle, beta
   * on a 2 contraintes :
   *     minimiser moy (v'w')
   *     rester "a peu près" vertical (moins de 10 deg.)
   */
  n_iter = 0;
  new_co_be = 1.0;
  do
    {
      co_be = new_co_be;

      /* calcul de si_be */
      sol1 = (-co_be + sqrt (co_be * co_be + 8 * K * K)) / (4 * K);
      sol2 = (-co_be - sqrt (co_be * co_be + 8 * K * K)) / (4 * K);
      if (fabs (sol1) > 1.0)
	{
	  if (fabs (sol2) > 1.0)
	    {
	      /* Aucune solution ->  sinus calculé simplement. */
	      si_be = copysign (sqrt (1 - (co_be * co_be)), si_be);
	    }
	  else
	    {			/* sol2 seule solution. */
	      si_be = sol2;
	    }
	}
      else
	{
	  if (fabs (sol2) > 1.0)
	    {			/* sol1 seule solution. */
	      si_be = sol1;
	    }
	  else
	    {			/* sol1 et sol2 sont possibles */
	      /* on choisit le plus petit angle */
	      if (fabs (sol1) < fabs (sol2))
		{
		  si_be = sol1;
		}
	      else
		{
		  si_be = sol2;
		}
	    }
	}
      /* Puis d'un co_be correspondant */
      new_co_be = sqrt (1 - si_be * si_be);
      if (new_co_be < 0.984807753)
	{			/* Blocage a 10 deg. */
	  new_co_be = 0.984807753;	/* cos (10 deg) */
	  /* sinus correspondant, en gardant le signe)   */
	  si_be = copysign (sqrt (1 - (new_co_be * new_co_be)), si_be);
	}
      n_iter++;
    }
  /* En double precision, on a plus de 7 chiffres significatifs.  */
  while (fabs (new_co_be - co_be) > 10.e-7);
  /* puisque new_co_be est quasi-égal à co_be, on peut garder l'un ou l'autre */
  fprintf (stderr, "niter=%lu\n", n_iter);

  /* Phase 1.5 : Application de la matrice de rotation correspondant à beta */
  {
    register double tmp_1, tmp_2;
    for (i = 0; i < NLoop; i++)
      {
	if (isfinite (u_r[i]) && isfinite (v_r[i]) && isfinite (w_r[i]))
	  {
	    tmp_1 = co_be * v_r[i] + si_be * w_r[i];
	    tmp_2 = -si_be * v_r[i] + co_be * w_r[i];

	    v_r[i] = tmp_1;
	    w_r[i] = tmp_2;
	  }
      }
  }
  info_tab[8] = atan2 (si_ep, co_ep);
  info_tab[9] = atan2 (si_th, co_th);
  info_tab[10] = atan2 (si_be, co_be);
  return ROT_OK;
}


/* la fonction d'enrobage classique */

int
OP_Rotat_rep_vent_moy (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  char TmpStr[100];
  double tab_ctrl[11];

  (void) sprintf (DiagExec,
                  "Rotat_rep_vent_moy, NbVal=%lu; ", NbVal);

  CodRet = Rotat_rep_vent_moy (NbVal,
			       (float *) ArgList[0],
			       (float *) ArgList[1],
			       (float *) ArgList[2],
			       1,
			       (float *) ArgList[3],
			       (float *) ArgList[4],
			       (float *) ArgList[5], tab_ctrl);

  switch (CodRet)
    {
    case ROT_NOVAL:
      (void) strcat (DiagExec, " WARNING : 0 valid data");
      return OP_OK;
      break;
    case ROT_OK:
      sprintf (TmpStr, "Moyennes sur %g valeurs (%g%%);",
	       tab_ctrl[0], 100.0 * tab_ctrl[0] / NbVal);
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, " Angles rotation = [%g, %g, %g] (deg);",
	       180 * tab_ctrl[8] / M_PI, 180 * tab_ctrl[9] / M_PI,
	       180 * tab_ctrl[10] / M_PI);
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, " APRES rotation :");
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, "moy(u_r)=%g (V_m=%g);", tab_ctrl[2], tab_ctrl[1]);
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, " moy(v_r)=%g;", tab_ctrl[3]);
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, " moy(w_r)=%g;", tab_ctrl[4]);
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, " var(v_r, w_r)=[%g,%g];", tab_ctrl[5], tab_ctrl[6]);
      strcat (DiagExec, TmpStr);
      sprintf (TmpStr, " covar(v_r, w_r)=%g;", tab_ctrl[7]);
      strcat (DiagExec, TmpStr);
      return OP_OK;
    }
  /* Si on arrive ici, on a eu un code-retour bizarre. */
  return OP_FAIL;
}

void
ID_Rotat_rep_vent_moy (oper * optr)
{
  strcpy (optr->Nom, "Rotat_rep_vent_moy");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Rotat_rep_vent_moy;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 6;

/*  Pour l'instant, les specifications d'unites sont
 * approximatives. L'ideal serait : Arg1.unit = "m/s OR kt".
 */
  /* u */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* v */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* w */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "any";

  /* u_r */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].misval = "$Arg1.misval";

  /* v_r */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";

  /* w_r */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";

}
