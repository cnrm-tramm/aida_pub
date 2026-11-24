/****************************************************
*
* OPERATOR     TKE.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul de l'energie cinetique turbulente
*
* DESCRIPTION  	Ce opérateur calcule TKE sur des périodes
*		de temps consécutives définies par l'utilisateur.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  x    Any      vecteur
*             IN   float  y    Any      vecteur
*             IN   float  z    Any      vecteur
*             IN   float  Fe   s-1	fréquence d'échantillonnage des données	
*             IN   float  Tint	s	Temps d'intégration pour le calcul des moyennes	
*             IN   float  rap_mnq 	souvent 0.5 (calcul si plus de la moitie des points)
*
*             OUT  float  tke	m**2/s**2	energie cinetique turbulente 
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

#include "struct_oper.h"

/* La vraie fonction... */

long
TKE (unsigned long Ndata,
     const float *x,
     const float *y,
     const float *z,
     const float Fe, const float Tint, const float rap_mnq, float *tke)
{
  long i, k, ntour, reste, nbpt, nbval_out;
  long mnq_xyz;

  register double fluct_x;
  register double fluct_y;
  register double fluct_z;

  double moy_x;
  double moy_y;
  double moy_z;

  double moy_fx2;
  double moy_fy2;
  double moy_fz2;

/* Calcul du nombre de points sur lequels on va calculer */

  /*nb de points sur la periode demandee */
  nbpt = floor ((Tint * Fe) + 0.5);
  /*fprintf (stderr, " nbpt= %ld \n", nbpt); */

  if (nbpt <= 0)
    return -1;

  /*******Calcul du nombre de tours***/
  ntour = Ndata / nbpt;
  reste = Ndata % nbpt;

  /* fprintf (stderr, " ntour= %ld, reste=%ld \n", ntour, reste); */

  for (k = 0; k < ntour; k++)
    {
/* on calcule d'abord les moyennes */

      moy_x = 0.;
      moy_y = 0.;
      moy_z = 0.;
      mnq_xyz = 0.;

      for (i = k * nbpt; i < (k + 1) * nbpt; i++)
	{
	  if (!isfinite (x[i]) || !isfinite (y[i]) || !isfinite (z[i]))
	    {
	      mnq_xyz = mnq_xyz + 1;
	    }
	  else
	    {
	      moy_x = moy_x + (double) x[i];
	      moy_y = moy_y + (double) y[i];
	      moy_z = moy_z + (double) z[i];
	    }
	}

      if (mnq_xyz > nbpt * rap_mnq)
	{
	  moy_x = K_NaN;
	  moy_y = K_NaN;
	  moy_z = K_NaN;
	}
      else
	{
	  moy_x = moy_x / ((double) (nbpt - mnq_xyz));
	  moy_y = moy_y / ((double) (nbpt - mnq_xyz));
	  moy_z = moy_z / ((double) (nbpt - mnq_xyz));
	}

/* on calcule les fluctuations*/

      fluct_x = 0. / 0.;
      fluct_y = 0. / 0.;
      fluct_z = 0. / 0.;
      moy_fx2 = 0.;
      moy_fy2 = 0.;
      moy_fz2 = 0.;
      mnq_xyz = 0.;

      for (i = k * nbpt; i < (k + 1) * nbpt; i++)
	{
	  if (!isfinite (x[i]) || !isfinite (y[i]) || !isfinite (z[i]))
	    {
	      /* mnq_xyz++; */
	      mnq_xyz = mnq_xyz + 1;
	      fluct_x = K_NaN;
	      fluct_y = K_NaN;
	      fluct_z = K_NaN;
	    }
	  else
	    {
	      fluct_x = (double) x[i] - moy_x;
	      fluct_y = (double) y[i] - moy_y;
	      fluct_z = (double) z[i] - moy_z;
	      /* on calcule les moyennes des carres des fluctuations */
	      moy_fx2 = moy_fx2 + fluct_x * fluct_x;
	      moy_fy2 = moy_fy2 + fluct_y * fluct_y;
	      moy_fz2 = moy_fz2 + fluct_z * fluct_z;
	    }
	}

      if (mnq_xyz > nbpt * rap_mnq)
	{
	  moy_fx2 = K_NaN;
	  moy_fy2 = K_NaN;
	  moy_fz2 = K_NaN;
	}
      else
	{
	  moy_fx2 = moy_fx2 / ((double) (nbpt - mnq_xyz));
	  moy_fy2 = moy_fy2 / ((double) (nbpt - mnq_xyz));
	  moy_fz2 = moy_fz2 / ((double) (nbpt - mnq_xyz));
	}


      /* On calcule la 1/2 somme */

      tke[k] = 1. / 2. * (float) (moy_fx2 + moy_fy2 + moy_fz2);
      /*
      fprintf (stderr, "TKE = %g\n", tke[k]);
      */

    }

  if (reste > 0)
    {
      tke[k] = 0. / 0.;
      k = k + 1;
    }

  nbval_out = k;
  return nbval_out;
}

/* la fonction d'enrobage classique */

int
OP_TKE (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;

  (void) sprintf (DiagExec,
		  "TKE, NbVal=%ld, Freq = %g, T. integration=%g, rap_mnq=%g\n",
		  NbVal,
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]), *((float *) ArgList[5]));

  CodRet = TKE (NbVal,
		(float *) ArgList[0],
		(float *) ArgList[1],
		(float *) ArgList[2],
		*((float *) ArgList[3]),
		*((float *) ArgList[4]),
		*((float *) ArgList[5]), (float *) ArgList[6]);
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
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
    }

}

void
ID_TKE (oper * optr)
{
  int i;

  strcpy (optr->Nom, "TKE");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_TKE;
  optr->NbArg = 7;
  optr->misval_auto = 1;

  /* x, y, z */
  for (i = 0; i <= 2; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "any";
    }
  for (i = 0; i <= 2; i++)
    {
      optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
    }

  /* Fe, Tint, rap_mnq */
  for (i = 3; i <= 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  /* tke */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal/($Arg4*$Arg5)";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "1./$Arg5";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg7.sample";
  optr->Arg_Car[6].unite = "$Arg1.unit $Arg1.unit";     /* une des syntaxe de multiplication d'unité */
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = " \"turbulence\" ";
  optr->Arg_Car[6].name = " \"Energie cinétique turbulente\" ";

}
