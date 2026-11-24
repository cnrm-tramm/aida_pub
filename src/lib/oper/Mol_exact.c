/****************************************************
*
* OPERATOR     Mol_exact.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul de la Longueur de Monin Obukov
*
* DESCRIPTION  	Cet opérateur calcule les covariances puis ustar et enfin Lmon. tson n'a pas forcement le m nb
*               de valeurs (a verifier : base de temps)   
*
* VERSION       %I%
*
*             IN   float  u     	m/s 	1ere composante horizontale du vent 
*             IN   float  v     	m/s	2eme composante horizontale du vent 
*             IN   float  w     	m/s	composante verticale du vent 
*             IN   float  tson    	C ou K	temperature issue du sonic
*             IN   float  tair	    	C ou K	temperature de l'air deduite du sonic et du licor	
*             IN   float  r     	g/kg	Rapport de mélange en vapeur d'eau (sonic + licor)
*             IN   float  Fe    	/s	fréquence d'échantillonnage des données	
*             IN   float  Tint		s	Temps d'intégration pour le calcul du flux	
*             IN   float  Tau		s	Constante de temps (generalement entre 200 et 600 sec) pour filtrage	
*             IN   float  rap_mnq 	souvent 0.5 (calcul si plus de la moitie des points)
*	      OUT  float  Lmon		m 	Longueur de Monin Obukhov
*	      OUT  float  Ustar		m/s 	vitesse de frottement
*	      OUT  float  Tstar		K 	temperature de flotabilite (rapport d'echelle)
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "thermo.h"
#include "unit_def.h"

#include "struct_oper.h"




/* La vraie fonction... */
long
Mol_exact (unsigned long Ndata,
	   const float *u,
	   const float *v,
	   const float *w,
	   const float *tson,
	   const float *tair,
	   const float *r, const float Fe, const float Tint, const float Tau,
	   const float rap_mnq, float *Lmon, float *Ustar, float *Tstar)
{
  long i, k, ntour, reste, nbpt, nbval_out;
  long binf, bsup;
  long mnq_wt;

  /*coefficients pour calcul de lmon */
  int flag_info;
  float C_to_K_moy;
  const float Kol = 0.4;
  const float g = 9.81;
  /*coefficients pour filtrage */
  register double b1, a1;
  register float memoire;

  /*declaration de la temperature : soit tson soit tair */
  float *t;
  /*declaration de la temperature filtree type FRC300 */
  float *tf;

  register double fluct_w;
  register double fluct_u;
  register double fluct_v;
  register double fluct_t;

  double moy_w, moy_u;
  double moy_v, moy_t;
  double moy_tf;
  double cov_wu;
  double cov_wv;
  double cov_wt;
  double ustar;
  double tstar;
  double lmon;

  flag_info = auto_tempe_unit (Ndata, tson, &C_to_K_moy);
  if (flag_info == MANQUANTES)
    return -1;

  /* Tau = 1./(2*M_PI*fc); */
  a1 = exp (-1.0 / Tau * Fe);
  /*a1 = exp (-1.0 * Te / Tau ); */
  b1 = 1.0 - a1;

  t = malloc (Ndata * sizeof (*t));
  tf = malloc (Ndata * sizeof (*tf));
  /*t = malloc ((Ndata + 1) * sizeof (*t)); */
  /*t = (float *)malloc(Ndata*sizeof(float)+1); */
  if (t == NULL)
    {
      fprintf (stderr, " Allocation impossible de t \n");
      /*fprintf (stderr, " t : %f \n", *t); */
      /*("Erreur d'allocation mémoire !!!"); */
      return -5;
    }

/* Calcul du nombre de points sur lequels on va calculer */

  /*nb de points sur la periode demandee */
  nbpt = floor ((Tint * Fe) + 0.5);
  fprintf (stderr, " nbpt= %ld \n", nbpt);

  if (nbpt <= 0)
    {
      free (t);
      free (tf);
      return -1;
    }

  /*******Calcul du nombre de tours***/
  ntour = Ndata / nbpt;
  reste = Ndata % nbpt;

  tf[0] = t[0];

  for (k = 0; k < ntour; k++)
    {
/* on calcule d'abord les moyennes */

      /*bornes sur chaque tour */
      binf = k * nbpt;
      bsup = (k + 1) * nbpt;

      moy_w = 0.;
      moy_u = 0.;
      moy_v = 0.;
      moy_t = 0.;
      moy_tf = 0.;
      /*   memoire = 0.; */
      mnq_wt = 0;

      for (i = binf; i < bsup; i++)
	{
	/******************************************/
	  /* Calcul de la temperature virtuelle */
	  /*Normalement, on devrait utiliser la temperature potentielle virtuelle tetav
	   * qui vaut teta*(1.0.61rap_air - rap_eau) avec rap_eau=0 si air non sature
	   * et teta=T*(Po/P)exp0.286 temperature potentielle seche ; mais on peut s'affranchir de la difference de pression dans notre cas
	   *  car elle est trop faible pour perturber le calcul*/

	  if (!isfinite (tair[i]) || !isfinite (r[i]))
	    /* on considere que tsonic est la meilleure approx de Tv */
	    {
	      t[i] = tson[i];
	      /*  fprintf (stderr, " t= %lf \n", t[i]); */
	    }
	  else
	    {
	      /* on prend T=Tv */
	      /* a verifier si cette formule s'applique sur t en celsius::?? */
	      t[i] =
		(tair[i]) * (1 + 1.608 * r[i] / 1000.) / (1 + r[i] / 1000.);
	    }
	/******************************************/


	  if (!isfinite (w[i]) || !isfinite (t[i]))
	    {
	      mnq_wt = mnq_wt + 1;
	      tf[i] = 0. / 0.;
	      if (isfinite (t[i - 1]))
		{
		  tf[i - 1] = t[i - 1];
		  memoire = tf[i - 1];
		}
	    }
	  else
	    {
	      moy_w = moy_w + (double) w[i];
	      moy_u = moy_u + (double) u[i];
	      moy_v = moy_v + (double) v[i];

	      if (!isfinite (t[i - 1]))
		{
		  tf[i] = a1 * memoire + b1 * t[i];
		}
	      else
		{
		  tf[i] = a1 * tf[i - 1] + b1 * t[i];
		}

	      moy_t = moy_t + (double) t[i];
	      moy_tf = moy_tf + (double) (t[i] - tf[i]);
	      /*fprintf (stderr, " moytf= %lf \n", moy_tf); */
	    }
	  /*fin de boucle sur i */
	}

      if (mnq_wt > nbpt * rap_mnq)	/* test sur t !ment */
	{
	  moy_w = K_NaN;
	  moy_u = K_NaN;
	  moy_v = K_NaN;
	  moy_t = K_NaN;
	  moy_tf = K_NaN;
	}
      else
	{
	  /*fprintf (stderr, " mnq_wt= %ld \n", mnq_wt); */
	  moy_w = moy_w / ((double) (nbpt - mnq_wt));
	  moy_u = moy_u / ((double) (nbpt - mnq_wt));
	  moy_v = moy_v / ((double) (nbpt - mnq_wt));
	  /*on calcule moy_t pour le calcul de lmon */
	  moy_t = moy_t / ((double) (nbpt - mnq_wt));
	  /*on calcule moy_tf pour le calcul des covariances */
	  moy_tf = moy_tf / ((double) (nbpt - mnq_wt));
	  /*fprintf (stderr, " moyt= %lf \n", moy_t); 
	     fprintf (stderr, " moytf= %lf \n", moy_tf); */
	}

/* on calcule les covariances et correlations*/

      cov_wu = 0.;
      cov_wv = 0.;
      cov_wt = 0.;
      mnq_wt = 0;

      for (i = binf; i < bsup; i++)
	{
	  if (!isfinite (w[i]) || !isfinite (tf[i]))
	    {
	      mnq_wt++;
	    }
	  else
	    {
	      fluct_w = (double) w[i] - moy_w;
	      fluct_u = (double) u[i] - moy_u;
	      fluct_v = (double) v[i] - moy_v;
	      fluct_t = (double) tf[i] - moy_tf;
	      cov_wu = cov_wu + fluct_w * fluct_u;
	      cov_wv = cov_wv + fluct_w * fluct_v;
	      cov_wt = cov_wt + fluct_w * fluct_t;
	    }
	}

      if (mnq_wt > nbpt * rap_mnq)
	{
	  cov_wu = K_NaN;
	  cov_wv = K_NaN;
	  cov_wt = K_NaN;
	}
      else
	{
	  cov_wu = cov_wu / (double) (nbpt - mnq_wt);
	  cov_wv = cov_wv / (double) (nbpt - mnq_wt);
	  cov_wt = cov_wt / (double) (nbpt - mnq_wt);

	  /* calcul de ustar */
	  /* ustar=sqrt(Cov_wu_wv); */
	  ustar = (double) sqrt (sqrt (cov_wu * cov_wu + cov_wv * cov_wv));

	  /* calcul de LMON */
	  /*Attention, ici les tempes sont en kelvin!!! */
	  /* LMON=-(ustar**3)*(Tvmoy)/(K*g*cov_wTvf); */
	  /*lmon=(double)(ustar*ustar*ustar)*(Tvmoy)/(Kol*g*cov_wt); */
	  lmon =
	    (double) (ustar * ustar * ustar) * (moy_t +
						C_to_K_moy) * (-1) / (Kol *
								      g *
								      cov_wt);
	  tstar = cov_wt * (-1) / ustar;
	  /*tstar=(double)(ustar*ustar)*(moy_t+C_to_K_moy)/(Kol*g*lmon); */
	  /*  fprintf (stderr, " covwt= %lf \n", cov_wt); */
	  /*  fprintf (stderr, " ustar= %lf \n", ustar); */

	}

      Lmon[k] = (float) lmon;
      Ustar[k] = (float) ustar;
      Tstar[k] = (float) tstar;
    }

  if (reste > 0)
    {
      Lmon[k] = 0. / 0.;
      Ustar[k] = 0. / 0.;
      Tstar[k] = 0. / 0.;
      k = k + 1;
    }

  nbval_out = k;
  free (t);
  free (tf);
  return nbval_out;
}

/* la fonction d'enrobage classique */

int
OP_Mol_exact (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Mol_exact : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Mol_exact (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3],
		      (float *) ArgList[4],
		      (float *) ArgList[5],
		      *((float *) ArgList[6]),
		      *((float *) ArgList[7]),
		      *((float *) ArgList[8]),
		      *((float *) ArgList[9]),
		      (float *) ArgList[10],
		      (float *) ArgList[11], 
              (float *) ArgList[12]);
  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK: %ld val. calculées.", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "; Nb resultats <= 0");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "; Bug interne : var_X < 0");
      return OP_FAIL;
    case -3:
      strcat (DiagExec, ";  Bug interne : var_Y < 0");
      return OP_FAIL;
    case -4:
      strcat (DiagExec, ";  Dephasage trop important");
      return OP_FAIL;
    case -5:
      strcat (DiagExec, ";  ERR: Allocation impossible pour t");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
    }

}

void
ID_Mol_exact (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Mol_exact");
  optr->Version = "%I%";
  optr->Date = "%G%";
  optr->fctptr = OP_Mol_exact;
  optr->NbArg = 13;
  optr->misval_auto = 1;

  for (i = 0; i <= 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "any";
    }

  for (i = 6; i <= 9; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal/($Arg7*$Arg8)";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "1./$Arg8";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time+\"_Med_%\"+$Arg8";
  /*optr->Arg_Car[10].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg8.sample"; */
  optr->Arg_Car[10].unite = "meter";
  optr->Arg_Car[10].misval = "$Arg1.misval";
  optr->Arg_Car[10].famille = " \"turbulence\" ";

  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal/($Arg7*$Arg8)";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "1./$Arg8";
  optr->Arg_Car[11].ref_time = "$Arg1.ref_time+\"_Med_%\"+$Arg8";
  optr->Arg_Car[11].unite = "meter/second";
  optr->Arg_Car[11].misval = "$Arg1.misval";
  optr->Arg_Car[11].famille = " \"turbulence\" ";

  optr->Arg_Car[12].direction = DIR_OUT;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].NbVal = "$Arg1.NbVal/($Arg7*$Arg8)";
  optr->Arg_Car[12].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[12].sample = "1./$Arg8";
  optr->Arg_Car[12].ref_time = "$Arg1.ref_time+\"_Med_%\"+$Arg8";
  optr->Arg_Car[12].unite = "kelvin";
  optr->Arg_Car[12].misval = "$Arg1.misval";
  optr->Arg_Car[12].famille = " \"turbulence\" ";

}
