/****************************************************
*
* OPERATOR     Covar_XY.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul des covariances et correlations entre 2 vecteurs
*
* DESCRIPTION  	Ce opérateur calcule les covariances et correlations sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  x    Any      premier vecteur
*             IN   float  y    Any      second vecteur
*             IN   float  Fe   s-1	fréquence d'échantillonnage des données	
*             IN   float  Tint	s	Temps d'intégration pour le calcul du flux	
*             IN   float  depha	s	dephasage entre le premier et le second vecteur	
*             IN   float  rap_mnq 	souvent 0.5 (calcul si plus de la moitie des points)
*
*             OUT  float  Cov_xy     x's unit * Y's unit Covariance 
*             OUT  float  Cor_xy     none		 Correlation
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

#include "struct_oper.h"

/* La vraie fonction... */

static float
sup (float x, float y)
{
  return (x < y) ? y : x;
}

static float
inf (float x, float y)
{
  return (x < y) ? x : y;
}

long
Covar_XY (unsigned long Ndata,
	  const float *x,
	  const float *y, const float Fe, const float Tint, const float depha,
	  const float rap_mnq, float *Cov_xy, float *Cor_xy)
{
  long i, j, k, ntour, reste, nbpt, nbval_out, nbpt_depha;
  long binf, bsup;
  long mnq_xy;
  float depha_n;

  register double fluct_x;
  register double fluct_y;

  double moy_x, moy_y;
  double var_x, var_y, cov_xy;
  double cor_xy;

/* Calcul du nombre de points sur lequels on va calculer */

  /*nb de points sur la periode demandee */
  nbpt = floor ((Tint * Fe) + 0.5);
  /*fprintf (stderr, " nbpt= %ld \n", nbpt); */

  if (nbpt <= 0)
    return -1;

  /*nb de points correspondant au dephasage */
  if (depha < 0)
    /*retard */
    {
      if (depha > -Tint / 2.)
	{
	  depha_n = -1 * depha;
	  nbpt_depha = floor ((depha_n * Fe) + 0.5);
	  nbpt_depha = -1 * nbpt_depha;
	}
      else
	{
	  nbpt_depha = 99999;
	}
    }
  else
    /*avance */
    {
      if (depha < Tint / 2.)
	{
	  nbpt_depha = floor ((depha * Fe) + 0.5);
	}
      else
	{
	  nbpt_depha = 99999;
	}
    }

  if (nbpt_depha >= 99999)
    return -4;

  /*fprintf (stderr, " nbpt_depha= %ld \n", nbpt_depha); */

  /*******Calcul du nombre de tours***/
  ntour = Ndata / nbpt;
  reste = Ndata % nbpt;

  /* fprintf (stderr, " ntour= %ld, reste=%ld \n", ntour, reste); */

  for (k = 0; k < ntour; k++)
    {
/* on calcule d'abord les moyennes */

      /*bornes sur chaque tour */
      binf = sup (k * nbpt, (k * nbpt) - nbpt_depha);
      bsup = inf ((k + 1) * nbpt, (k + 1) * nbpt - nbpt_depha);

      moy_x = 0.;
      moy_y = 0.;
      mnq_xy = 0;

      for (i = binf; i < bsup; i++)
	{
	  /*on decale de nbpt_depha points */
	  j = i + nbpt_depha;

	  if (!isfinite (x[i]) || !isfinite (y[j]))
	    /*if (!isfinite (x[i]) || !isfinite (y[j]) || j < binf || j >= bsup) */
	    {
	      mnq_xy = mnq_xy + 1;
	    }
	  else
	    {
	      moy_x = moy_x + (double) x[i];
	      moy_y = moy_y + (double) y[j];
	    }
	}

      if (mnq_xy > nbpt * rap_mnq)
	{
	  moy_x = K_NaN;
	  moy_y = K_NaN;
	}
      else
	{
	  moy_x = moy_x / ((double) (nbpt - mnq_xy));
	  /*fprintf (stderr, " moyx= %lf \n", moy_x); */
	  moy_y = moy_y / ((double) (nbpt - mnq_xy));
	  /*fprintf (stderr, " moyy= %lf \n", moy_y); */
	}

/* on calcule les covariances et correlations*/

      cov_xy = 0.;
      var_x = 0.;
      var_y = 0.;
      mnq_xy = 0;

      /*for (i = k * nbpt; i < (k + 1) * nbpt; i++) */
      for (i = binf; i < bsup; i++)
	{
	  /*on decale de nbpt_depha points */
	  j = i + nbpt_depha;

	  if (!isfinite (x[i]) || !isfinite (y[j]))
	    /*if (!isfinite (x[i]) || !isfinite (y[j]) || j < binf || j >= bsup) */
	    {
	      mnq_xy++;
	    }
	  else
	    {
	      fluct_x = (double) x[i] - moy_x;
	      fluct_y = (double) y[j] - moy_y;
	      cov_xy = cov_xy + fluct_x * fluct_y;
	      var_x = var_x + fluct_x * fluct_x;
	      var_y = var_y + fluct_y * fluct_y;
	      cor_xy = cov_xy / (sqrt (var_x) * sqrt (var_y));
	    }
	}

      if (mnq_xy > nbpt * rap_mnq)
	{
	  var_x = K_NaN;
	  var_y = K_NaN;
	  cov_xy = K_NaN;
	}
      else
	{
	  cov_xy = cov_xy / (double) (nbpt - mnq_xy);
	  var_x = var_x / (double) (nbpt - mnq_xy);
	  var_y = var_y / (double) (nbpt - mnq_xy);
	}

      if (var_x < 0)
	return -2;
      if (var_y < 0)
	return -3;


      /*fprintf (stderr, "cov_xy = %g\n", cov_xy); */

      Cov_xy[k] = (float) cov_xy;
      Cor_xy[k] = (float) cor_xy;
    }

  if (reste > 0)
    {
      Cov_xy[k] = 0. / 0.;
      Cor_xy[k] = 0. / 0.;
      k = k + 1;
    }

  nbval_out = k;
  return nbval_out;
}

/* la fonction d'enrobage classique */

int
OP_Covar_XY (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Covar_XY : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Covar_XY (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *((float *) ArgList[2]),
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]),
		     *((float *) ArgList[5]),
		     (float *) ArgList[6], (float *) ArgList[7]);
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
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
    }

}

void
ID_Covar_XY (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Covar_XY");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Covar_XY;
  optr->NbArg = 8;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  for (i = 2; i <= 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "1./$Arg4";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg7.sample";
  optr->Arg_Car[6].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = " \"auto\" ";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "1./$Arg4";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg8.sample";
  optr->Arg_Car[7].unite = "without";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].famille = " \"auto\" ";

}
