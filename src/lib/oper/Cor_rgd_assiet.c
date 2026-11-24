/*************************************************************************
*
* OPERATOR         Cor_rgd_assiet.c  FUNCTION ANSI-C
*
* PURPOSE          Correction d'assiette pour le flux sw descendant
*
*
* DESCRIPTION      Appel d'une fonction de G. Brogniez (LOA)
*
* VERSION          1.0
*
* ARGUMENTS
*          IN   int     dv                 JDA (numéro du Jour Dans l'Année)
*          IN   double  t       sec        Temps UTC (sec depuis 0h du jour JDA)
*          IN   float   lon     degree     longitude
*          IN   float   lat     degree     latitude
*          IN   float   Psi	degree     Heading
*          IN   float   Phi     degree     Roll Attitude angle
*          IN   float   Theta	degree     Pitch attitude angle
*          IN   float   offroul degree     Roll angle offset between INS and pyranometer
*          IN   float   offtang degree     Pitch angle offset between INS and pyranometer
*          IN   float   SWDOWN  W/m2       Flux SW descendant brut

*          OUT  float   SWCOR   W/m2       Flux SW descendant corrigé de l'attitude
*
*
* ENTRY        NONE
*
* SUBPROGRAMS  Appel de la routine FORTRAN du LOA : possol
*
* REFERENCES
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques
*	       GMEI/TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex 1
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"
#include "oper_util.h"
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


/* Déclaration de la routine en FORTRAN */
#include "corassiet.h"

typedef struct
{
  unsigned long nb_incl_sup;
  unsigned long nb_brut_inf;
  unsigned long nb_brut_sup;
  unsigned long nb_cor_inf;
  unsigned long nb_cor_sup;
}
cr_exec_t;


static cr_exec_t
Cor_rgd_assiet (unsigned long ndata, const int *jda,	/* Jour de l'année, 1--366 */
		const double *t,	/* Nombre de secondes depuis 0h00 */
		const float *lon, const float *lat, 
		const float *psi,	/* Cap ou azimut */
		const float *phi,   	/* Roulis ou angle de gîte */
		const float *theta,   /* Tangage ou assiette longitudinale */
		const double *offroul,	/* Décalage roulis, en degrés */
		const double *offtang,	/* Décalage tangage, en degrés */
		const float *swdown, float *swcor)
{
  unsigned long i;
  static cr_exec_t CR;
  double loc_lon, loc_lat, loc_psi, loc_phi, loc_theta;
  double loc_offroul, loc_offtang;
  double loc_swdown, loc_swcor;
  double t_phi, t_theta, incl_tot;
/* Les valeurs ci-dessous sont en W/m2.
   * A convertir si utilisation d'une autre unité
   *
   * Ces valeurs viennent des recommandations du BSRN Global Network
   * (http://bsrn.awi.de/fileadmin/user_upload/redakteur/Publications/BSRN_recommended_QC_tests_V2.pdf)
   *  min = -4, fixe
   *  max = f(sza), pris ici pour sza=0 (cos(sza)=1).
   */
  const float max_incl = 9;
  const float min_swdown = -4;
  const float max_swdown = 1362 * 1.5 + 100;

  CR.nb_incl_sup = 0;
  CR.nb_brut_inf = 0;
  CR.nb_brut_sup = 0;
  CR.nb_cor_inf = 0;
  CR.nb_cor_sup = 0;
  for (i = 0; i < ndata; i++)
    {
      t_phi = tan (phi[i] * M_PI / 180.);
      t_theta = tan (theta[i] * M_PI / 180.);
      incl_tot =
	180.0 / M_PI * atan (sqrt (t_phi * t_phi + t_theta * t_theta));
      if (incl_tot > max_incl)
	{
	  swcor[i] = K_NaN;
	  CR.nb_incl_sup += 1;
	  continue;
	}

      /* Conversion de type de paramètres d'entrée */
      loc_lon = lon[i];
      loc_lat = lat[i];
      loc_psi = psi[i];
      loc_phi = phi[i];
      loc_theta = theta[i];
      loc_offroul = *offroul;
      loc_offtang = *offtang;

      if (swdown[i] < min_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_brut_inf += 1;
	  continue;
	}
      if (swdown[i] > max_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_brut_sup += 1;
	  continue;
	}
      loc_swdown = swdown[i];

      /* appel de la fonction écrite en Fortran.  */
      assiet (jda, &(t[i]), &loc_lon, &loc_lat, &loc_psi, &loc_phi,
	      &loc_theta, &loc_offroul, &loc_offtang, &loc_swdown,
	      &loc_swcor);

      /* Contrôle et conversion de type de paramètres de sortie */
      /* A faire : il faudra récupérer le SZA, et calculer
       * max_swdown = 1362 * 1.5 * cos(SZA)^1.2 + 100 */
      if (loc_swcor < min_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_cor_inf += 1;
	}
      else if (loc_swcor > max_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_cor_sup += 1;
	}
      else
	swcor[i] = loc_swcor;
    }
  return CR;
}

/* Ancienne version, buguée, de la fonction Cor_rgd_assiet, conservée
 * uniquement pour être capable de caractériser l'impact du bug.
 */
static cr_exec_t
Cor_rgd_assiet_bug (unsigned long ndata, const int *jda,	/* Jour de l'année, 1--366 */
		    const double *t,	/* Nombre de secondes depuis 0h00 */
		    const float *lon, const float *lat, const float *psi,	/* Cap ou azimut */
		    const float *phi,	/* Tangage ou assiette longitudinale */
		    const float *theta,	/* Roulis ou angle de gîte */
		    const double *offroul,	/* Décalage roulis, en degrés */
		    const double *offtang,	/* Décalage tangage, en degrés */
		    const float *swdown, float *swcor)
{
  unsigned long i;
  static cr_exec_t CR;
  double loc_lon, loc_lat, loc_psi, loc_phi, loc_theta;
  double loc_offroul, loc_offtang;
  double loc_swdown, loc_swcor;
  double t_phi, t_theta, incl_tot;
/* Les valeurs ci-dessous sont en W/m2.
   * A convertir si utilisation d'une autre unité
   *
   * Ces valeurs viennent des recommandations du BSRN Global Network
   * (http://bsrn.awi.de/fileadmin/user_upload/redakteur/Publications/BSRN_recommended_QC_tests_V2.pdf)
   *  min = -4, fixe
   *  max = f(sza), pris ici pour sza=0 (cos(sza)=1).
   */
  const float max_incl = 9;
  const float min_swdown = -4;
  const float max_swdown = 1362 * 1.5 + 100;

  CR.nb_incl_sup = 0;
  CR.nb_brut_inf = 0;
  CR.nb_brut_sup = 0;
  CR.nb_cor_inf = 0;
  CR.nb_cor_sup = 0;
  for (i = 0; i < ndata; i++)
    {
      t_phi = tan (phi[i] * M_PI / 180.);
      t_theta = tan (theta[i] * M_PI / 180.);
      incl_tot =
	180.0 / M_PI * atan (sqrt (t_phi * t_phi + t_theta * t_theta));
      if (incl_tot > max_incl)
	{
	  swcor[i] = K_NaN;
	  CR.nb_incl_sup += 1;
	  continue;
	}

      if (swdown[i] > max_swdown)
	/* Conversion de type de paramètres d'entrée */
	loc_lon = lon[i];
      loc_lat = lat[i];
      loc_psi = psi[i];
      loc_phi = phi[i];
      loc_theta = theta[i];
      loc_offroul = *offroul;
      loc_offtang = *offtang;

      if (swdown[i] < min_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_brut_inf += 1;
	  continue;
	}
      if (swdown[i] > max_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_brut_sup += 1;
	  continue;
	}
      loc_swdown = swdown[i];

      /* appel de la fonction écrite en Fortran.  */
      assiet (jda, &(t[i]), &loc_lon, &loc_lat, &loc_psi, &loc_phi,
	      &loc_theta, &loc_offroul, &loc_offtang, &loc_swdown,
	      &loc_swcor);

      /* Contrôle et conversion de type de paramètres de sortie */
      /* A faire : il faudra récupérer le SZA, et calculer
       * max_swdown = 1362 * 1.5 * cos(SZA)^1.2 + 100 */
      if (loc_swcor < min_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_cor_inf += 1;
	}
      else if (loc_swcor > max_swdown)
	{
	  swcor[i] = K_NaN;
	  CR.nb_cor_sup += 1;
	}
      else
	swcor[i] = loc_swcor;
    }
  return CR;
}


/* la fonction d'enrobage classique */
int
OP_Cor_rgd_assiet (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;
  cr_exec_t CR;

/* Attention OFROL et OFTAG sont theoriquement figes pour un avion donne
C Les valeurs ci-dessous correspondent au F20
c      OFROL=-0.3D+00
c      OFTAG=-1.3D+00 */

  NCar =
    sprintf (DiagExec,
	     "Cor_rgd_assiet (%ld ech, jour=%d, decalages roulis=%g; tangage=%g)",
	     NbVal,
	     *((int *) ArgList[0]),
	     *((double *) ArgList[7]), *((double *) ArgList[8]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, " temps", (double *) ArgList[1],
				 NbVal);
  CR = Cor_rgd_assiet (NbVal,
		       (int *) ArgList[0],
		       (double *) ArgList[1],
		       (float *) ArgList[2],
		       (float *) ArgList[3],
		       (float *) ArgList[4],
		       (float *) ArgList[5],
		       (float *) ArgList[6],
		       (double *) ArgList[7],
		       (double *) ArgList[8],
		       (float *) ArgList[9], (float *) ArgList[10]);

  sprintf (DiagExec,
	   ", Rejets : incl_sup:%lu, brut_inf:%lu, brut_sup:%lu, cor_inf:%lu, cor_sup:%lu",
	   CR.nb_incl_sup, CR.nb_brut_inf, CR.nb_brut_sup, CR.nb_cor_inf,
	   CR.nb_cor_sup);

  return OP_OK;
}

int
OP_Cor_rgd_assiet_bug (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;
  cr_exec_t CR;

  NCar =
    sprintf (DiagExec,
	     "Cor_rgd_assiet_bug (jour=%d, decalages roulis=%g; tangage=%g)",
	     *((int *) ArgList[0]),
	     *((double *) ArgList[7]), *((double *) ArgList[8]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, " temps", (double *) ArgList[1],
				 NbVal);
  CR = Cor_rgd_assiet_bug (NbVal,
			   (int *) ArgList[0],
			   (double *) ArgList[1],
			   (float *) ArgList[2],
			   (float *) ArgList[3],
			   (float *) ArgList[4],
			   (float *) ArgList[5],
			   (float *) ArgList[6],
			   (double *) ArgList[7],
			   (double *) ArgList[8],
			   (float *) ArgList[9], (float *) ArgList[10]);

  sprintf (DiagExec,
	   ", Rejets : incl_sup:%lu, brut_inf:%lu, brut_sup:%lu, cor_inf:%lu, cor_sup:%lu",
	   CR.nb_incl_sup, CR.nb_brut_inf, CR.nb_brut_sup, CR.nb_cor_inf,
	   CR.nb_cor_sup);

  return OP_OK;
}


void
ID_Cor_rgd_assiet (oper * optr)
{
  int idx;

  strcpy (optr->Nom, "Cor_rgd_assiet");
  optr->Version = "$Revision: 5414 $";
  optr->Date = "$Date: 2013-09-27 17:38:37 +0200 (ven. 27 sept. 2013) $";
  optr->fctptr = OP_Cor_rgd_assiet;
  optr->NbArg = 11;		/* doit rester inf. a FIL_MAX_ARG */

  /* jda */
  idx = 0;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_I32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "day";

  /* UTC */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "s";

  /* lon */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "degree";

  /* lat */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[idx].unite = "degree";

  /*  psi : Cap ou azimut */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[idx].unite = "degree";

  /*  phi : Roulis ou angle de gîte */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[idx].unite = "degree";

  /* theta : Pitch, tangage, assiette longitudinale */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[idx].unite = "degree";

  /* offroul */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].unite = "degree";

  /* offtang */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].unite = "degree";

  /*  sw_down */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[idx].unite = "W/m2";

  /*  sw_cor :  */
  idx++;
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg10.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg10.type_sample";
  optr->Arg_Car[idx].sample = "$Arg10.sample";
  optr->Arg_Car[idx].ref_time = "$Arg10.ref_time";
  optr->Arg_Car[idx].unite = "$Arg10.unit";
  optr->Arg_Car[idx].misval = "$Arg10.misval";
  optr->Arg_Car[idx].famille = " \"rayonnement\" ";
  optr->Arg_Car[idx].name = "$Arg10.name + \" corrige de l'attitude\" ";
  optr->Arg_Car[idx].en_name =
    "$Arg10.english_name + \" corrected for attitude\" ";

  if (idx != optr->NbArg - 1)
    {
      fprintf (stderr,
	       "Bug interne %s : incoherence NbArg declare (%d) et compte (%d)\n",
	       "ID_Cor_rgd_assiet", optr->NbArg, idx);
    }
}


void
ID_Cor_rgd_assiet_bug (oper * optr)
{
  ID_Cor_rgd_assiet (optr);
  strcpy (optr->Nom, "Cor_rgd_assiet_bug");
  optr->fctptr = OP_Cor_rgd_assiet_bug;
}
