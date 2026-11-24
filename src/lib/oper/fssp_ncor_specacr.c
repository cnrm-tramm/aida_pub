/*******************************************************************
* OPERATOR      fssp_ncor_specacr.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du nombre total de gouttelettes 
*		corrige des coincidences. 
*
* DESCRIPTION   La methode de correction utilise le temps
*		de transit "tauspec" estime a partir du
*		spectre de gouttes mesure, et d'une part
*		l'activite, et d'autre part le taux de 
*		comptage.  
*
* VERSION       1.0
*
*		IN 	float 	strobe		nombre de particules dans la DOF
*		IN	float 	reset		nombre de particules total dans et hors de la DOF  
*		IN	float 	activity	activite (s)
*               IN      float   tauspec		temps de transit estime a 
*						partir du spectre de gouttes(s)
*		IN 	float   fr 		frequency (Hz) 
*		IN 	float   tau1		delai court de l'electronique (s) 
*		IN 	float   tau2		delai long de l'electronique (s) 
*		IN 	float   taur		reset (s) 
*		IN	float 	crt0		seuil de taux de comptage pour la correction
*						de coincidence
*
*               OUT     float   ntot_ac  	nombre de particules total corrige 
*						a partir de l'activite
*		OUT	float 	ntot_rs		nombre de particules total corrige
*					 	a partir du taux de comptage
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	  
*		Coincidence and Dead-Time Corrections for Particle Counters.
*		Part I : A general Mathematical Formalism. J-L Brenguier and L. Amodei 
*               Part II : High concentration Measurements with an FSSP. J-L Brenguier 
*		Journal of Atmos. and Ocean. Technolology, Vol 6, No 4, August 1989
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"
#include "fssp_eqn.h"

int
fssp_ncor_specacr (unsigned long ndata,
		   float *strobe,
		   float *reset,
		   float *activity,
		   float *tauspec,
		   float fr,
		   float tau1,
		   float tau2,
		   float taur, 
                   float crt0, 
                   float *ntot_ac, 
                   float *ntot_rs)
{
  unsigned long i;

  int iacrt /* , itau*/ ;

  float expm = 0.367879;
  float tau, DOF;
  float dcrt, crt, crt1, crt2, crtx;
  float dAc, Ac, Al1, Al2;
  float acrt, dacrt, iter_acrt, acrtx;
  float Tbar1, Tbar2;
  float XX, signe;

  FILE *fp;

  fp = fopen ("./trt_fssp_specacr.log", "w");
  if (fp == NULL)
    {
      fp = stderr;
    }

  for (i = 0; i < ndata; i++)
    {

/*** calcul de la DOF ***/
      if (reset[i] * fr < crt0)
	{
	  ntot_ac[i] = 0.;
	  ntot_rs[i] = 0.;
	  continue;
	}
      DOF = strobe[i] / reset[i];

/************************************************/
/*** premiere correction utilisant l'activite ***/

/*** initialisation avant l'iteration  ***/
      tau = tauspec[i];
      iacrt = 0;
      acrt = reset[i] * fr;
      dacrt = 0.2 * acrt;
      iter_acrt = 1.;

     /**********************************************
     iteration sur le taux de comptage 
     tant que l'activite n'est pas egale a l'activite
     mesuree ***/

      dAc = 1.;
      while (fabs (dAc) > 0.01)
	{
	  acrt = acrt + iter_acrt * dacrt;
	  iacrt = iacrt + 1;

/*** calcul de l'activite et du tau de comptage ***/
	  equ2 (acrt, tau, tau1, tau2, taur, &Tbar2, &crt2, &Al2);
	  equ1 (acrt, tau, tau1, taur, &Tbar1, &crt1, &Al1);

	  crt = 1. / (((1. - DOF) / crt1) + (DOF / crt2));
	  Ac = crt * ((1. - DOF) * (Tbar1 + tau1 - Al1)
		      + DOF * (Tbar2 + tau2 - Al2));

	  dAc = 1. - (activity[i] / Ac);
/*** stop iteration si ca ne converge pas assez vite ***/
	  if (fabs (dacrt) < 0.001 * acrt)
	    {
	      fprintf (fp, "*** %lu : Stop after %d iterations\n", i, iacrt);
	      fprintf (fp, "Relative error on activity is : %g\n", dAc);
	      break;
	    }
	  if (dAc * iter_acrt >= 0.)
	    {
	      dacrt = dacrt * 0.5;
	      iter_acrt = -1. * iter_acrt;
	    }
	}
      ntot_ac[i] = acrt / fr;

/*****************************************************/
/*** 2eme correction utilisant le taux de comptage ***/

     /*** 2 solutions sont possibles : la solution choisie est
     celle qui est la plus proche de la solution trouvee avec
     l'activite ***/

      tau = tauspec[i];

     /*** calcul du taux de comptage maximum ***/

      acrtx = 1. / tau;
      XX = expm * acrtx;
      crt2 = XX;
      if (tau2 > tau)
	crt2 = XX / (1. + XX * (tau2 - tau));
      crt1 = XX;
      if (tau1 > tau)
	crt1 = XX / (1. + XX * (tau1 - tau));

      crtx = 1. / (((1. - DOF) / crt1) + (DOF / crt2));

      if ((reset[i] * fr) > crtx)
	{
	  /* pas de solution */
	  fprintf (fp,
		   "**** %lu : No solution for the counted rate approach \n",
		   i);
	  fprintf (fp, "Counted rate measured is too high\n");
	  ntot_rs[i] = acrtx / fr;
	  continue;
	}

     /*** iteration du taux de comptage jusqu'a que ce que le
     taux de comptage mesure et calcule soient suffisament proches ***/

      iacrt = 0;
      dacrt = 0.2 * acrtx;
      iter_acrt = 1.;

      if ((fr * ntot_ac[i]) <= acrtx)
	{
	  acrt = reset[i] * fr;
	  signe = 1.;
	}
      else
	{
	  acrt = ntot_ac[i] * fr;
	  signe = -1.;
	}

      dcrt = 0.56;		/* N'importe quelle valeur > 0.01 */
      while (fabs (dcrt) > 0.01)
	{
	  acrt = acrt + iter_acrt * dacrt;
	  /*** 01/04/2009: je ne comprends pas l'interet de ce test a la con (?)
	   * mais il faut le suprimer car en forcant actr, on maintient dcrt
	   * constant, et donc ca boucle !! (Fred)
	  if ((signe * (acrtx - acrt)) < 0.)
	    acrt = acrtx; ***/
	  if (acrt <= 1.)
	    acrt = 1.;
	  iacrt = iacrt + 1;

/*** calcul du taux de comptage ***/
	  equ2 (acrt, tau, tau1, tau2, taur, &Tbar2, &crt2, &Al2);
	  equ1 (acrt, tau, tau1, taur, &Tbar1, &crt1, &Al1);

	  crt = 1. / (((1. - DOF) / crt1) + (DOF / crt2));

	  dcrt = 1. - ((reset[i] * fr) / crt);
/*** stop iteration si ca ne converge pas assez vite ***/
	  if (fabs (dacrt) < 0.001 * acrt)
	    {
	      fprintf (fp, "*** %lu : Stop after %d iterations\n", i, iacrt);
	      fprintf (fp, "Relative error on counted rate : %g\n", dAc);
	      break;
	    }

	  if (dcrt * iter_acrt > 0.)
	    {
	      dacrt = 0.5 * dacrt;
	      iter_acrt = -1. * iter_acrt;
	    }
	}
      ntot_rs[i] = acrt / fr;

    }

  fclose (fp);

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_ncor_specacr (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;

  NCar = sprintf (DiagExec, 
"OP_fssp_ncor_specacr (%ld, .., .., .., .., %g, %g, %g, %g, %g, .., ..)",
		  NbVal, *((float *) ArgList[4]),
		  *((float *) ArgList[5]), *((float *) ArgList[6]), 
		  *((float *) ArgList[7]), *((float *) ArgList[8]));

  (void) fssp_ncor_specacr (NbVal,
			  (float *) ArgList[0],
			  (float *) ArgList[1],
			  (float *) ArgList[2],
			  (float *) ArgList[3],
			  *((float *) ArgList[4]),
			  *((float *) ArgList[5]),
			  *((float *) ArgList[6]),
			  *((float *) ArgList[7]),
			  *((float *) ArgList[8]),
			  (float *) ArgList[9],
			  (float *) ArgList[10]);
  return OP_OK;
}

void
ID_fssp_ncor_specacr (oper * optr)
{
  strcpy (optr->Nom, "fssp_ncor_specacr");
  optr->Version = "1.0";
  optr->Date = "10/28/96";
  optr->fctptr = OP_fssp_ncor_specacr;
  optr->NbArg = 11;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "second";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "Hz";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "second";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "second";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "second";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "second-1";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "";
  optr->Arg_Car[9].famille = "\"microphysique\"";
  optr->Arg_Car[9].name = 
    "\"nombre total de particules, corrige a partir de l'activite\"";

  /* ntot_rs */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "";
  optr->Arg_Car[10].famille = "\"microphysique\"";
  optr->Arg_Car[10].name = 
    "\"nombre total de particules, corrige a partir du taux de comptage\"";
}
