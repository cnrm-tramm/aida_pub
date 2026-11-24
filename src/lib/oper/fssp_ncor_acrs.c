/*******************************************************************
* OPERATOR      fssp_ncor_acrs.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du nombre total de gouttelettes 
*		corrige des coincidences. 
*
* DESCRIPTION   La methode utilise la combinaison 
*               de l'activite et du taux de comptage.	
*		Elle calcule le temps de transit et le 
*		taux de comptage corrige.
*
* VERSION       1.0
*
*		IN 	float 	strobe		nombre de particules dans la DOF
*		IN	float 	reset		nombre de particules total
*           					dans et hors de la DOF  
*		IN	float 	activity	activite (s)
*               IN      float   Tbar		temps de transit moyen  (s)
*		IN 	float   fr 		frequency (Hz) 
*		IN 	float   tau1		delai court de l'electronique (s) 
*		IN 	float   tau2		delai long de l'electronique (s) 
*		IN 	float   taur		reset (s) 
*		IN 	float 	crt0		seuil de taux de comptage pour la
*						correction de coincidence 
*
*               OUT     float   ntot_acrs       nombre de particules total corrige 
*		OUT	float 	tau_acrs 	temps de transit calcule
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
fssp_ncor_acrs (unsigned long ndata,
		float *strobe,
		float *reset,
		float *activity,
		float *Tbar,
		float fr,
		float tau1,
		float tau2,
		float taur,
                float crt0,
                float *ntot_acrs,
                float *tau_acrs)
{
  unsigned long i;

  int iacrt, itau;

  float DOF;
  float tau, dtau, iter_tau;
  float dcrt, crt, crt1, crt2;
  float dAc, Ac, Al1, Al2;
  float acrt, dacrt, iter_acrt;
  float Tbar1, Tbar2;

  FILE *fp;

  fp = fopen ("/tmp/aida_log/trt_fssp_acrs.log", "w");
  if (fp == NULL)
    {
      fp = fopen ("./trt_fssp_acrs.log", "w");
      if (fp == NULL)
	{
	  fp = stderr;
	}
    }

  for (i = 0; i < ndata; i++)
    {
      if (reset[i] * fr < crt0)
	{
	  ntot_acrs[i] = 0.;
	  tau_acrs[i] = 0.;
	  continue;
	}
      DOF = strobe[i] / reset[i];

      /*** initialisation avant l'iteration  ***/
      tau = Tbar[i];
      dtau = 0.1 * Tbar[i];
      iter_tau = -1.;

     /**********************************************
      * iteration sur le temps de transit "tau"  
      * tant que le taux de comptage n'est pas le meme 
      * que la mesure ***/

      dcrt = 1.;
      while (fabs (dcrt) > 0.01)
	{
	  tau = tau + iter_tau * dtau;
	  itau = itau + 1;

	  acrt = reset[i] * fr;
	  dacrt = 0.2 * acrt;
	  iter_acrt = 1.;

	  /*** 01/04/09: je deplace ce test ici car dans la boucle suivante
	   * le break ne suffit pas pour passer a la data suivante
	   * et donc ca boucle !! (Fred)
	   * "continue" serait peut-être mieux ?
	   ***/

	  if ((tau <= 0.1e-6) && (iter_tau < 0.))
	    {
		  /** fprintf (fp, "data: %ld  \n", i );
		  fprintf (fp, "**** tau is too small : %g\n", tau); **/
	      fprintf (stderr, "**** %lu tau is too small : %g\n", i, tau);
	      ntot_acrs[i] = 0.;
	      tau_acrs[i] = 0.;
	      break;
	    }
/***
        fprintf ( stderr, "%d acrt : %f dacrt : %f iter_acrt : %f dcrt : %f \n", i, acrt, dacrt, iter_acrt, dcrt); 
        fprintf ( stderr, "%d crt : %f Ac : %f dAc : %f \n", i, crt, Ac, dAc); 
        fprintf ( stderr, " Tbar : %e , tau : %e, iter_tau : %f \n", Tbar[i], tau, iter_tau);
        fprintf ( stderr, " Activity : %f , dAc : %f \n", activity[i], dAc); 
***/
	/**********************************************
        iteration sur le taux de comptage corrige "acrt"
        tant que l'activite n'est pas la meme que celle
        mesuree ***/

	  iacrt = 0;
	  dAc = 1.;
	  while (fabs (dAc) > 0.01)
	    {
	      acrt = acrt + iter_acrt * dacrt;
	      iacrt = iacrt + 1;

              /*** calcul de l'activite et du taux de comptage ***/
	      equ2 (acrt, tau, tau1, tau2, taur, &Tbar2, &crt2, &Al2);
	      equ1 (acrt, tau, tau1, taur, &Tbar1, &crt1, &Al1);

	      crt = 1. / (((1. - DOF) / crt1) + (DOF / crt2));
	      Ac = crt * ((1. - DOF) * (Tbar1 + tau1 - Al1)
			  + DOF * (Tbar2 + tau2 - Al2));

	      dAc = 1. - (activity[i] / Ac);

              /*** stop iteration si ca ne converge pas assez vite ***/
	      if (fabs (dacrt) < 0.001 * acrt)
		{
		  fprintf (fp, "***Stop after %d iterations\n", iacrt);
		  fprintf (fp, "Relative error on activity is : %g\n", dAc);
		  break;
		}
	      if (dAc * iter_acrt >= 0.)
		{
		  dacrt = dacrt * 0.5;
		  iter_acrt = -1. * iter_acrt;
		}
	    }

	  dcrt = 1. - ((reset[i] * fr) / crt);
          /*** stop iteration si ca ne converge pas assez vite ***/
	  if (fabs (dtau) < 0.001 * tau)
	    {
	      fprintf (fp, "data: %ld  \n", i);
	      fprintf (fp, "***Stop after %d iterations\n", iacrt);
	      fprintf (fp, "Relative error on counted rate is : %g\n", dcrt);
	      break;
	    }
	  if (dcrt * iter_tau <= 0.)
	    {
	      dtau = dtau * 0.5;
	      iter_tau = -1. * iter_tau;
	    }
	}

      ntot_acrs[i] = acrt / fr;
      tau_acrs[i] = tau;
    }

  fclose (fp);
  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_ncor_acrs (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  (void) fssp_ncor_acrs (Nbval,
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
ID_fssp_ncor_acrs (oper * optr)
{
  strcpy (optr->Nom, "fssp_ncor_acrs");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_ncor_acrs;
  optr->NbArg = 11;

  /* strobe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* reset */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* activity */
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

  /* ntot_acrs */
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
  optr->Arg_Car[9].name = "\"nombre de particules total corrige\"";
  optr->Arg_Car[9].en_name = "\"Corrected total particule number\"";

  /* tau_acrs */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "second";
  optr->Arg_Car[10].famille = "\"microphysique\"";
  optr->Arg_Car[10].name = "\"temps de transit calcule\"";
  optr->Arg_Car[10].en_name = "\"Computed transit time\"";
}
