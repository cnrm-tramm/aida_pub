/****************************************************
*
* OPERATOR     Covar_XY_ctl.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul des covariances et correlations entre 2 vecteurs
*
* DESCRIPTION  	Ce opérateur calcule les covariances et correlations sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*		A la difference de l'operateur Covar_XY : il calcule la covariance dans 
*		tous les cas et fournit le nombre de secondes ayant servies au calcul.
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN   float  x    		Any    				premier vecteur
*             IN   float  y    		Any    				second vecteur
*             IN   float  Fe   		s-1				fréquence d'échantillonnage des données	
*             IN   float  Tint	 	s				Temps d'intégration pour le calcul du flux	
*
*             OUT  float  Cov_xy        x's unit * Y's unit            	Covariance 
*             OUT  float  Cor_xy        none		               	Correlation
*             OUT  float  Nbsec_valid   s                              	nombre de secondes valides sur lequel la covariance a été calculée 
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
Covar_XY_ctl (unsigned long Ndata,
	  const float *x,
	  const float *y, const float Fe, const float Tint,
	  float *Cov_xy, float *Cor_xy, float *Nbsec_valid)
{
  long i, k, ntour, reste, nbpt_int, nbpt_xy, nbval_out;
  long binf, bsup;

  register double fluct_x;
  register double fluct_y;

  double moy_x, moy_y;
  double var_x, var_y, cov_xy;
  double cor_xy;

/* Calcul du nombre de points sur lequels on va calculer */

  /*nb de points sur la periode demandee */
  nbpt_int = floor ((Tint * Fe) + 0.5);
  /*fprintf (stderr, " nbpt= %ld \n", nbpt_int); */

  if (nbpt_int <= 0)
    return -1;


  /*******Calcul du nombre de tours***/
  ntour = Ndata / nbpt_int;
  reste = Ndata % nbpt_int;

  /* fprintf (stderr, " ntour= %ld, reste=%ld \n", ntour, reste); */

  for (k = 0; k < ntour; k++)
    {
/* on calcule d'abord les moyennes */

      /*bornes sur chaque tour */
      binf = k * nbpt_int;
      bsup = (k + 1)*nbpt_int;

      moy_x = 0.;
      moy_y = 0.;
      nbpt_xy = 0;

      for (i = binf; i < bsup; i++)
	{
	  if (isfinite (x[i]) && isfinite (y[i]))
	    {
	      moy_x = moy_x + (double) x[i];
	      moy_y = moy_y + (double) y[i];
	      nbpt_xy = nbpt_xy + 1;
	    }
	}

      if ( nbpt_xy == 0 )
	{
	  moy_x = K_NaN;
	  moy_y = K_NaN;
	}
      else
	{
	  moy_x = moy_x / ((double) (nbpt_xy));
	  /*fprintf (stderr, " moyx= %lf \n", moy_x);*/ 
	  moy_y = moy_y / ((double) (nbpt_xy));
	  /*fprintf (stderr, " moyy= %lf \n", moy_y); */
	}

/* on calcule les covariances et correlations*/

      cov_xy = 0.;
      var_x = 0.;
      var_y = 0.;
      nbpt_xy = 0;

      for (i = binf; i < bsup; i++)
	{
	  if (isfinite (x[i]) && isfinite (y[i]) )
	    {
	      fluct_x = (double) x[i] - moy_x;
	      fluct_y = (double) y[i] - moy_y;
	      cov_xy = cov_xy + fluct_x * fluct_y;
	      var_x = var_x + fluct_x * fluct_x;
	      var_y = var_y + fluct_y * fluct_y;
	      cor_xy = cov_xy / (sqrt (var_x) * sqrt (var_y));
	      nbpt_xy = nbpt_xy +1;
	    }
	}

      if (nbpt_xy == 0 )
	{
	  var_x = K_NaN;
	  var_y = K_NaN;
	  cov_xy = K_NaN;
	  cor_xy = K_NaN;
	}
      else
	{
	  cov_xy = cov_xy / (double) (nbpt_xy);
	  var_x = var_x / (double) (nbpt_xy);
	  var_y = var_y / (double) (nbpt_xy);
	}

      if (var_x < 0)
	return -2;
      if (var_y < 0)
	return -3;


      /*fprintf (stderr, "cov_xy = %g\n", cov_xy); */

      Cov_xy[k] = (float) cov_xy;
      Cor_xy[k] = (float) cor_xy;
      Nbsec_valid[k] = (float) nbpt_xy / Fe ;
    }

  if (reste > 0)
    {
      Cov_xy[k] = 0. / 0.;
      Cor_xy[k] = 0. / 0.;
      Nbsec_valid[k] = 0 ;
      k = k + 1;
    }

  nbval_out = k;
  return nbval_out;
}

/* la fonction d'enrobage classique */

int
OP_Covar_XY_ctl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Covar_XY_ctl : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Covar_XY_ctl (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *((float *) ArgList[2]),
		     *((float *) ArgList[3]),
		     (float *) ArgList[4],
		     (float *) ArgList[5],
		     (float *) ArgList[6] );
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
ID_Covar_XY_ctl (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Covar_XY_ctl");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Covar_XY_ctl;
  optr->NbArg = 7;
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

  for (i = 2; i <= 3; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "1./$Arg4";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg5.sample";
  optr->Arg_Car[4].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].famille = "\"auto\"";
  optr->Arg_Car[4].name = "\"Covariance  \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[4].en_name = "\"Covariance  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "1./$Arg4";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg6.sample";
  optr->Arg_Car[5].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].famille = "\"auto\"";
  optr->Arg_Car[5].name = "\"Correlation  \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[5].en_name = "\"Correlation  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "1./$Arg4";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg7.sample";
  optr->Arg_Car[6].unite = "second";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = "\"controle\"";
  optr->Arg_Car[6].name = "\"Nombre de secondes pour le calcul de la covariance : \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[6].en_name = "\"Number of seconds in calculation of covariance  : \" + $Arg1.english_name + \".\" + $Arg2.english_name";

}
