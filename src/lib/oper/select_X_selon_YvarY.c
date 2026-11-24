/*********************************************************
* OPERATOR 	select_X_selon_YvarY.c FUNCTION ANSI-C
*
* PURPOSE       Selectionne les valeurs d'un vecteur X si 
*		   - les valeurs du vecteur Y
*		sont dans une fourchette de validité donnée.
*		   - il n'y a pas de variation de Y à t-Tau_av, et à à Tau_ap 
*	   	 
*		Cet opérateur remplace les valeurs "invalides" par 
*		la valeur invalide choisie par l'utilisateur (valeur manquante le + souvent).
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	X		vecteur à valider 
*		IN 	float	Y   		vecteur servant à valider X 
*		IN 	double  freq_ech	frequence d'échantillonnage de X
*		IN	float 	Y_inf		valeur min tolérée de Y 
*		IN 	float 	Y_sup		valeur max tolérée de Y
*		IN 	float 	Delta_Y		valeur de variation de Y au delà de laquelle on invalide la données
*		IN 	float	Tau_av		temps pendant lequel on ivalide les données avant une variation de Y > delta_Y 
*		IN 	float	Tau_ap		temps pendant lequel on invalide les données après une variation de Y > delta_Y  
*		IN 	float 	Y_mnq		valeur correspondant à la valeur mnq du vecteur Y
*						si celle-ci est différente de NaN (ex : -32000, -999...)
*		IN 	float 	inv_val	 	valeur de remplacement de X, le + souvent valeur
*						manquante (ex : -32000, -999...)
*
*		OUT 	float 	X_valid		vecteur X "validé" en sortie 
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
* 		C.Berne 29/08/2006
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

unsigned long
select_X_selon_YvarY (unsigned long Nloop,
		      const float *X,
		      const float *Y,
		      const double freq_ech,
		      const float Y_inf,
		      const float Y_sup,
		      const float Delta_Y,
		      const float Tau_av,
		      const float Tau_ap,
		      const float Y_mnq,
		      const float inv_val,
		      float *X_valid, unsigned long *Diag_tab)
{
  unsigned long i, k, idx_av_saut, idx_ap_saut;
  unsigned long nb_sup, nb_inf, nb_mnq, nb_NaN_X, nb_NaN_Y, nb_ok, nb_dY;

  int flag_variationY;

  /*********************************************************
   * Initialisation des compteurs de valeurs trop ...
   * grandes, trop petites, égales à Y_mnq ou à NaN ...
   * ou "correctes" 
   * *******************************************************/
  nb_sup = 0;
  nb_inf = 0;
  nb_mnq = 0;
  nb_NaN_X = 0;
  nb_NaN_Y = 0;
  nb_dY = 0;
  nb_ok = 0;
  flag_variationY = 0;

  /***********************************************************
   Le vecteur X est considere bon si ces criteres sont verifies :
	1) Y[i] - Y[i-1] > Delta_Y entre (time[i]-Tau_av) et (time[i] + Tau_ap) 
   	2) Y_inf <= Y <= Y_sup
   	3) Y est different de Y_mnq (au cas où)
   	4) Y est different de NaN (valeur infinie...) , test souvent
	redondant avec Y différent de Y_mnq mais au cas où... !

   Le critère 1) est prioritaire par rapport aux critère 2).

  ************************************************************/

  /* Traitement de la 1ere valeur à qui on applique 
   * uniquement les critères 2, 3, 4 */

  if (isfinite (Y[0]))
    {
      if (Y[0] > Y_sup)
	{
	  X_valid[0] = inv_val;
	  nb_sup = nb_sup + 1;
	}
      else if (Y[0] < Y_inf)
	{
	  X_valid[0] = inv_val;
	  nb_inf = nb_inf + 1;
	}
      else if (Y[0] == Y_mnq)
	{
	  X_valid[0] = inv_val;
	  nb_mnq = nb_mnq + 1;
	}
      else if (!isfinite (X[0]))
	{
	  /* On met la valeur inv_val dans X_valid, car
	   * il y a une petite bug de WriteVect qui écrit des NaN
	   * à la place de la valeur choisie pour "mnq" (dans entete) */
	  nb_NaN_X = nb_NaN_X + 1;
	  X_valid[0] = inv_val;
	}
      else
	{
	  X_valid[0] = X[0];
	  nb_ok = nb_ok + 1;
	}
    }
  else
    /* Si Y est NaN , on le comptabilise comme tel !  */
    {
      X_valid[0] = inv_val;
      nb_NaN_Y = nb_NaN_Y + 1;
    }

  for (i = 1; i < Nloop; i++)
    {
      if ((isfinite (Y[i])) && (isfinite (Y[i - 1]))
	  && (fabsf (Y[i] - Y[i - 1]) > Delta_Y))
	{
	  /* cas d'un saut de Y superieur au seuil Delta_Y
	   * on invalide les données à t-Tau_av avant le saut de Y */
	  flag_variationY = 1;
	  idx_av_saut = i - floor (Tau_av * freq_ech);
	  if (idx_av_saut < 0)
	    idx_av_saut = 0;
	  idx_ap_saut = i + floor (Tau_ap * freq_ech);
	  if (idx_ap_saut > Nloop - 1)
	    idx_ap_saut = Nloop - 1;
	  for (k = idx_av_saut; k <= i; k++)
	    {
	      X_valid[k] = inv_val;
	      nb_dY = nb_dY + 1;
	    }
	}
      else
	{
	  if ((flag_variationY == 1) && (i < idx_ap_saut))
	    /* on est à moins de t+Tau_ap après la variation de Y on invalide les données */
	    {
	      X_valid[i] = inv_val;
	      nb_dY = nb_dY + 1;
	    }
	  else
	    {
	      /* on est à plus de T+Tau_ap après la variation de Y 
	         on teste si  Y est compris dans [Y_inf, Y_sup] */
	      flag_variationY = 0;
	      if (isfinite (Y[i]))
		{
		  if (Y[i] > Y_sup)
		    {
		      X_valid[i] = inv_val;
		      nb_sup = nb_sup + 1;
		    }
		  else if (Y[i] < Y_inf)
		    {
		      X_valid[i] = inv_val;
		      nb_inf = nb_inf + 1;
		    }
		  else if (Y[i] == Y_mnq)
		    {
		      X_valid[i] = inv_val;
		      nb_mnq = nb_mnq + 1;
		    }
		  else if (!isfinite (X[i]))
		    {
		      /* On met la valeur inv_val dans X_valid, car
		       * il y a une petite bug de WriteVect qui écrit des NaN
		       * à la place de la valeur choisie pour "mnq" (dans entete) */
		      nb_NaN_X = nb_NaN_X + 1;
		      X_valid[i] = inv_val;
		    }
		  else
		    {
		      X_valid[i] = X[i];
		      nb_ok = nb_ok + 1;
		    }
		}
	      else
		/* Si Y est NaN , on le comptabilise comme tel !  */
		{
		  X_valid[i] = inv_val;
		  nb_NaN_Y = nb_NaN_Y + 1;
		}
	    }
	}
    }
  /*  On renvoie les compteurs d'anomalies pour l'entete du nouveau vecteur */
  Diag_tab[0] = nb_ok;
  Diag_tab[1] = nb_sup;
  Diag_tab[2] = nb_inf;
  Diag_tab[3] = nb_dY;
  Diag_tab[4] = nb_mnq;
  Diag_tab[5] = nb_NaN_X;
  Diag_tab[6] = nb_NaN_Y;
  return nb_sup + nb_inf + nb_mnq + nb_NaN_Y + nb_dY;
}

/* fonction d'enrobage */

int
OP_select_X_selon_YvarY (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;
  unsigned long Diag_tab[7];

  NCar = sprintf (DiagExec,
		  "select_X_selon_YvarY (%lu ech), %g<Y<%g, |Delta_Y|<%g",
		  Nbval, *((float *) ArgList[2]), *((float *) ArgList[3]),
		  *((float *) ArgList[4]));
  DiagExec += (NCar < 0 ? 0 : NCar);

  CodRet = select_X_selon_YvarY (Nbval,
				 (float *) ArgList[0],
				 (float *) ArgList[1],
				 *((double *) ArgList[2]),
				 *((float *) ArgList[3]),
				 *((float *) ArgList[4]),
				 *((float *) ArgList[5]),
				 *((float *) ArgList[6]),
				 *((float *) ArgList[7]),
				 *((float *) ArgList[8]),
				 *((float *) ArgList[9]),
				 (float *) ArgList[10], Diag_tab);

  sprintf (DiagExec, ", %lu valeurs acceptée(s) [dont %lu sont NaN] \
 -et- %lu valeurs (sur %lu) rejetée(s)  \
 [sup:%lu, inf:%lu, dY :%lu, mnq_Y:%lu, nan_Y:%lu, ]", Diag_tab[0], Diag_tab[4], CodRet, Nbval, Diag_tab[1], Diag_tab[2], Diag_tab[3], Diag_tab[5], Diag_tab[6]);

  return OP_OK;
}

void
ID_select_X_selon_YvarY (oper * optr)
{
  strcpy (optr->Nom, "select_X_selon_YvarY");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_X_selon_YvarY;
  optr->NbArg = 11;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Y */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  /* Les deux variables doivent être synchrones */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[1].unite = "any";

  /* freq_ech */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";

  /* Y_inf */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";

  /* Y_sup */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";

  /* Delta_Y */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";

  /* Tau_av */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";

  /* Tau_ap */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";

  /* Y_mnq */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].unite = "without";

  /* inv_val */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";

  /* X_valid */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[10].unite = "$Arg1.unit";
  optr->Arg_Car[10].famille = "$Arg1.famille";
  optr->Arg_Car[10].misval = "$Arg10";
  optr->Arg_Car[10].name =
    "\"Select \"+ $Arg1.name + \" avec \" + $Arg2.name + \" et ses variations \" ";
  optr->Arg_Car[10].en_name =
    "\"Select \"+ $Arg1.english_name + \" whith \" + $Arg2.english_name + \"  and when its value changes \" ";
}
